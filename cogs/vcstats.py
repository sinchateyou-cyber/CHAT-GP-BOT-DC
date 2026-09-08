import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import time
from pathlib import Path
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "vcstats.json"
REQUIRED_SECONDS = 60 * 60  # 1 hora
DEFAULT_ROLE_NAME = "CHARLATAN 🎤"
CHECK_INTERVAL = 30  # segundos
# ============================================================
# UTILIDADES JSON
# ============================================================
def ensure_data():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )
def load_data():
    ensure_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except (json.JSONDecodeError, OSError):
        return {}
def save_data(data):
    ensure_data()
    temp_file = DATA_FILE.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )
    temp_file.replace(DATA_FILE)
# ============================================================
# COG
# ============================================================
class VCStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Usuario -> momento en el que entró a VC
        self.active_sessions = {}
        # Evita procesar dos veces el mismo premio
        self.reward_given = set()
        # Inicia el sistema de comprobación
        self.check_voice_time.start()
    # ========================================================
    # CLEANUP
    # ========================================================
    def cog_unload(self):
        self.check_voice_time.cancel()
    # ========================================================
    # OBTENER DATOS DEL SERVIDOR
    # ========================================================
    def get_guild_data(self, guild_id):
        data = load_data()
        guild_id = str(guild_id)
        if guild_id not in data:
            data[guild_id] = {
                "users": {},
                "role_id": None
            }
        return data
    # ========================================================
    # OBTENER ROL CHARLATAN
    # ========================================================
    async def get_charlatan_role(self, guild):
        data = load_data()
        guild_id = str(guild.id)
        if guild_id not in data:
            data[guild_id] = {
                "users": {},
                "role_id": None
            }
        role_id = data[guild_id].get("role_id")
        # Intentar usar el rol guardado
        if role_id:
            role = guild.get_role(int(role_id))
            if role:
                return role
        # Buscar por nombre
        role = discord.utils.get(
            guild.roles,
            name=DEFAULT_ROLE_NAME
        )
        if role:
            data[guild_id]["role_id"] = role.id
            save_data(data)
            return role
        # Crear automáticamente
        try:
            role = await guild.create_role(
                name=DEFAULT_ROLE_NAME,
                reason="Rol automático de VCStats por alcanzar 1 hora en VC."
            )
            data[guild_id]["role_id"] = role.id
            save_data(data)
            return role
        except discord.Forbidden:
            return None
        except discord.HTTPException:
            return None
    # ========================================================
    # AÑADIR TIEMPO
    # ========================================================
    async def add_voice_time(self, member, seconds):
        if seconds <= 0:
            return
        data = load_data()
        guild_id = str(member.guild.id)
        user_id = str(member.id)
        if guild_id not in data:
            data[guild_id] = {
                "users": {},
                "role_id": None
            }
        if "users" not in data[guild_id]:
            data[guild_id]["users"] = {}
        if user_id not in data[guild_id]["users"]:
            data[guild_id]["users"][user_id] = {
                "seconds": 0,
                "reward": False
            }
        user_data = data[guild_id]["users"][user_id]
        user_data["seconds"] = int(
            user_data.get("seconds", 0)
        ) + int(seconds)
        save_data(data)
        # Comprobar recompensa
        if (
            user_data["seconds"] >= REQUIRED_SECONDS
            and not user_data.get("reward", False)
        ):
            await self.give_charlatan(member)
    # ========================================================
    # DAR CHARLATAN
    # ========================================================
    async def give_charlatan(self, member):
        guild = member.guild
        role = await self.get_charlatan_role(guild)
        if role is None:
            print(
                f"[VCStats] No pude crear/encontrar "
                f"el rol {DEFAULT_ROLE_NAME} en {guild.name}"
            )
            return
        # Ya tiene el rol
        if role in member.roles:
            data = load_data()
            guild_id = str(guild.id)
            user_id = str(member.id)
            if guild_id in data and user_id in data[guild_id]["users"]:
                data[guild_id]["users"][user_id]["reward"] = True
                save_data(data)
            return
        try:
            await member.add_roles(
                role,
                reason="Alcanzó 1 hora acumulada en canales de voz."
            )
            data = load_data()
            guild_id = str(guild.id)
            user_id = str(member.id)
            if guild_id not in data:
                data[guild_id] = {
                    "users": {},
                    "role_id": role.id
                }
            if user_id not in data[guild_id]["users"]:
                data[guild_id]["users"][user_id] = {
                    "seconds": REQUIRED_SECONDS,
                    "reward": True
                }
            else:
                data[guild_id]["users"][user_id]["reward"] = True
            data[guild_id]["role_id"] = role.id
            save_data(data)
            print(
                f"[VCStats] 🎤 {member} recibió "
                f"{DEFAULT_ROLE_NAME} en {guild.name}"
            )
        except discord.Forbidden:
            print(
                f"[VCStats] No tengo permisos para darle "
                f"{DEFAULT_ROLE_NAME} a {member}."
            )
        except discord.HTTPException as e:
            print(
                f"[VCStats] Error dando rol a {member}: {e}"
            )
    # ========================================================
    # COMPROBAR SI ESTÁ EN VOZ
    # ========================================================
    def is_valid_voice_session(self, member):
        voice = member.voice
        if voice is None:
            return False
        if voice.channel is None:
            return False
        # No contar AFK
        if member.guild.afk_channel:
            if voice.channel.id == member.guild.afk_channel.id:
                return False
        return True
    # ========================================================
    # EVENTO DE CAMBIO DE VOZ
    # ========================================================
    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):
        before_channel = before.channel
        after_channel = after.channel
        # ----------------------------------------------------
        # ENTRA A VC
        # ----------------------------------------------------
        if before_channel is None and after_channel is not None:
            if not self.is_valid_voice_session(member):
                return
            key = (
                member.guild.id,
                member.id
            )
            self.active_sessions[key] = time.time()
        # ----------------------------------------------------
        # SALE DE VC
        # ----------------------------------------------------
        elif before_channel is not None and after_channel is None:
            key = (
                member.guild.id,
                member.id
            )
            start_time = self.active_sessions.pop(
                key,
                None
            )
            if start_time is not None:
                elapsed = time.time() - start_time
                await self.add_voice_time(
                    member,
                    elapsed
                )
        # ----------------------------------------------------
        # CAMBIA DE CANAL
        # ----------------------------------------------------
        elif (
            before_channel is not None
            and after_channel is not None
            and before_channel.id != after_channel.id
        ):
            key = (
                member.guild.id,
                member.id
            )
            start_time = self.active_sessions.get(key)
            if start_time is not None:
                elapsed = time.time() - start_time
                await self.add_voice_time(
                    member,
                    elapsed
                )
            # Reiniciar sesión
            if self.is_valid_voice_session(member):
                self.active_sessions[key] = time.time()
            else:
                self.active_sessions.pop(
                    key,
                    None
                )
    # ========================================================
    # LOOP DE CONTROL
    # ========================================================
    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_voice_time(self):
        current_time = time.time()
        for key, start_time in list(
            self.active_sessions.items()
        ):
            guild_id, user_id = key
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                continue
            member = guild.get_member(user_id)
            if member is None:
                self.active_sessions.pop(
                    key,
                    None
                )
                continue
            # Si salió de VC
            if not self.is_valid_voice_session(member):
                self.active_sessions.pop(
                    key,
                    None
                )
                continue
            # Calcular tiempo de esta sesión
            elapsed = current_time - start_time
            # Guardar cada intervalo
            if elapsed >= CHECK_INTERVAL:
                await self.add_voice_time(
                    member,
                    elapsed
                )
                # Reiniciar contador de sesión
                self.active_sessions[key] = current_time
    @check_voice_time.before_loop
    async def before_check_voice_time(self):
        await self.bot.wait_until_ready()
    # ========================================================
    # /VCSTATS
    # ========================================================
    @commands.hybrid_command(
        name="vcstats",
        description="Muestra cuánto tiempo llevás en canales de voz."
    )
    @app_commands.describe(
        usuario="Usuario que querés consultar."
    )
    async def vcstats(
        self,
        ctx,
        usuario: discord.Member = None
    ):
        usuario = usuario or ctx.author
        data = load_data()
        guild_id = str(ctx.guild.id)
        user_id = str(usuario.id)
        seconds = 0
        if guild_id in data:
            if user_id in data[guild_id].get("users", {}):
                seconds = data[guild_id]["users"][user_id].get(
                    "seconds",
                    0
                )
        # Si está actualmente conectado, mostrar también
        # el tiempo de la sesión actual.
        key = (
            ctx.guild.id,
            usuario.id
        )
        if key in self.active_sessions:
            current_session = (
                time.time()
                - self.active_sessions[key]
            )
            seconds += int(current_session)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        remaining = max(
            0,
            REQUIRED_SECONDS - seconds
        )
        remaining_minutes = int(
            remaining // 60
        )
        role = await self.get_charlatan_role(
            ctx.guild
        )
        has_reward = False
        if role and role in usuario.roles:
            has_reward = True
        embed = discord.Embed(
            title="🎤 VCStats",
            description=(
                f"**Usuario:** {usuario.mention}\n\n"
                f"⏱️ **Tiempo total:** "
                f"`{hours}h {minutes}m {secs}s`\n"
            ),
            color=discord.Color.blurple()
        )
        if has_reward:
            embed.add_field(
                name="🎤 Recompensa",
                value=(
                    f"Ya tenés el rol "
                    f"**{DEFAULT_ROLE_NAME}**."
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 Próxima recompensa",
                value=(
                    f"Te faltan aproximadamente "
                    f"**{remaining_minutes} minutos** "
                    f"para conseguir **{DEFAULT_ROLE_NAME}**."
                ),
                inline=False
            )
        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )
        await ctx.send(
            embed=embed
        )
    # ========================================================
    # /SETCHARLATAN
    # ========================================================
    @commands.hybrid_command(
        name="setcharlatan",
        description="Configura el rol que se entrega al llegar a 1 hora en VC."
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    @app_commands.describe(
        rol="Rol que querés usar como CHARLATAN."
    )
    async def setcharlatan(
        self,
        ctx,
        rol: discord.Role
    ):
        # El bot no puede administrar un rol igual o superior
        # a su rol más alto.
        if ctx.guild.me and rol >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ No puedo usar ese rol porque está "
                "por encima o al mismo nivel que mi rol más alto.",
                ephemeral=True
            )
            return
        data = load_data()
        guild_id = str(ctx.guild.id)
        if guild_id not in data:
            data[guild_id] = {
                "users": {},
                "role_id": None
            }
        data[guild_id]["role_id"] = rol.id
        save_data(data)
        await ctx.send(
            f"✅ El rol de **CHARLATAN 🎤** ahora es {rol.mention}."
        )
    # ========================================================
    # /RESETVCSTATS
    # ========================================================
    @commands.hybrid_command(
        name="resetvcstats",
        description="Reinicia las estadísticas de VC de un usuario."
    )
    @commands.has_guild_permissions(
        administrator=True
    )
    @app_commands.describe(
        usuario="Usuario al que querés reiniciar."
    )
    async def resetvcstats(
        self,
        ctx,
        usuario: discord.Member
    ):
        data = load_data()
        guild_id = str(ctx.guild.id)
        user_id = str(usuario.id)
        if guild_id in data:
            if user_id in data[guild_id].get(
                "users",
                {}
            ):
                data[guild_id]["users"][user_id] = {
                    "seconds": 0,
                    "reward": False
                }
                save_data(data)
        # Sacar sesión activa si existe
        self.active_sessions.pop(
            (
                ctx.guild.id,
                usuario.id
            ),
            None
        )
        await ctx.send(
            f"🔄 Se reiniciaron las estadísticas de VC de "
            f"{usuario.mention}."
        )
    # ========================================================
    # /TOPVC
    # ========================================================
    @commands.hybrid_command(
        name="topvc",
        description="Muestra el ranking de tiempo en canales de voz."
    )
    async def topvc(self, ctx):
        data = load_data()
        guild_id = str(ctx.guild.id)
        users = data.get(
            guild_id,
            {}
        ).get(
            "users",
            {}
        )
        ranking = []
        for user_id, user_data in users.items():
            seconds = int(
                user_data.get(
                    "seconds",
                    0
                )
            )
            ranking.append(
                (
                    int(user_id),
                    seconds
                )
            )
        # Agregar sesiones activas
        now = time.time()
        for (
            key,
            start_time
        ) in self.active_sessions.items():
            active_guild_id, user_id = key
            if active_guild_id != ctx.guild.id:
                continue
            active_seconds = int(
                now - start_time
            )
            found = False
            for index, (
                existing_id,
                seconds
            ) in enumerate(ranking):
                if existing_id == user_id:
                    ranking[index] = (
                        existing_id,
                        seconds + active_seconds
                    )
                    found = True
                    break
            if not found:
                ranking.append(
                    (
                        user_id,
                        active_seconds
                    )
                )
        ranking.sort(
            key=lambda x: x[1],
            reverse=True
        )
        ranking = ranking[:10]
        if not ranking:
            await ctx.send(
                "📊 Todavía no hay estadísticas de VC."
            )
            return
        description = ""
        medals = [
            "🥇",
            "🥈",
            "🥉"
        ]
        for index, (
            user_id,
            seconds
        ) in enumerate(ranking):
            member = ctx.guild.get_member(
                user_id
            )
            if member is None:
                continue
            hours = int(
                seconds // 3600
            )
            minutes = int(
                (seconds % 3600) // 60
            )
            if index < 3:
                prefix = medals[index]
            else:
                prefix = f"`#{index + 1}`"
            description += (
                f"{prefix} {member.mention} "
                f"— **{hours}h {minutes}m**\n"
            )
        embed = discord.Embed(
            title="🎤 TOP VC",
            description=description,
            color=discord.Color.blurple()
        )
        await ctx.send(
            embed=embed
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    ensure_data()
    await bot.add_cog(
        VCStats(bot)
    )