# cogs/jailed.py

import json
from pathlib import Path

import discord
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "jailed.json"

JAILED_ROLE_NAME = "JAILED"


# ============================================================
# UTILIDADES
# ============================================================

def ensure_data_folder():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def load_data():
    ensure_data_folder()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

            if isinstance(data, dict):
                return data

            return {}

    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data):
    ensure_data_folder()

    temp_file = DATA_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    temp_file.replace(DATA_FILE)


# ============================================================
# COG
# ============================================================

class Jailed(commands.Cog):
    """
    Sistema de Jail / Unjail.

    Comandos:
    /jailed @usuario [razón]
    /unjail @usuario
    """

    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ========================================================
    # OBTENER ROL JAILED
    # ========================================================

    async def get_jailed_role(self, guild: discord.Guild):

        role = discord.utils.get(
            guild.roles,
            name=JAILED_ROLE_NAME
        )

        if role:
            return role

        try:
            role = await guild.create_role(
                name=JAILED_ROLE_NAME,
                reason="Creación automática del sistema de Jail"
            )

            print(
                f"[JAILED] Rol creado en {guild.name}: "
                f"{role.name} ({role.id})"
            )

            return role

        except discord.Forbidden:
            return None

        except discord.HTTPException as e:
            print(
                f"[JAILED] Error creando rol en "
                f"{guild.name}: {e}"
            )
            return None

    # ========================================================
    # EMBED DE ERROR
    # ========================================================

    def error_embed(self, texto):
        return discord.Embed(
            description=f"❌ {texto}",
            color=discord.Color.red()
        )

    # ========================================================
    # EMBED DE ÉXITO
    # ========================================================

    def success_embed(self, texto):
        return discord.Embed(
            description=f"✅ {texto}",
            color=discord.Color.green()
        )

    # ========================================================
    # PERMISOS DEL MODERADOR
    # ========================================================

    def can_moderate(
        self,
        moderator: discord.Member,
        target: discord.Member,
        bot_member: discord.Member
    ):

        # Dueño del servidor
        if target.id == moderator.guild.owner_id:
            return False, "No podés encarcelar al dueño del servidor."

        # Intentar moderarse a sí mismo
        if target.id == moderator.id:
            return False, "No podés encarcelarte a vos mismo."

        # El bot no puede actuar sobre sí mismo
        if target.id == bot_member.id:
            return False, "No puedo encarcelarme a mí mismo."

        # Jerarquía del moderador
        if (
            moderator.id != moderator.guild.owner_id
            and target.top_role >= moderator.top_role
        ):
            return False, (
                "No podés actuar sobre alguien con un rol "
                "igual o superior al tuyo."
            )

        # Jerarquía del bot
        if target.top_role >= bot_member.top_role:
            return False, (
                "Mi rol está por debajo o al mismo nivel que "
                "el rol más alto de ese usuario."
            )

        return True, None

    # ========================================================
    # JAILED
    # ========================================================

    @commands.hybrid_command(
        name="jailed",
        description="Manda a un usuario a la cárcel."
    )
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def jailed(
        self,
        ctx: commands.Context,
        usuario: discord.Member,
        *,
        razon: str = "Sin razón especificada"
    ):

        guild = ctx.guild

        if guild is None:
            return

        # ----------------------------------------------------
        # BOT
        # ----------------------------------------------------

        bot_member = guild.me

        if bot_member is None:
            bot_member = guild.get_member(self.bot.user.id)

        if bot_member is None:
            await ctx.send(
                embed=self.error_embed(
                    "No pude encontrar mi usuario dentro del servidor."
                ),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # PERMISOS
        # ----------------------------------------------------

        permitido, error = self.can_moderate(
            ctx.author,
            usuario,
            bot_member
        )

        if not permitido:
            await ctx.send(
                embed=self.error_embed(error),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # ROL JAILED
        # ----------------------------------------------------

        jailed_role = await self.get_jailed_role(guild)

        if jailed_role is None:
            await ctx.send(
                embed=self.error_embed(
                    "No pude crear/encontrar el rol `JAILED`. "
                    "Verificá que tenga permiso para gestionar roles."
                ),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # JERARQUÍA DEL ROL
        # ----------------------------------------------------

        if jailed_role >= bot_member.top_role:
            await ctx.send(
                embed=self.error_embed(
                    "El rol `JAILED` está por encima de mi rol. "
                    "Mové mi rol por encima de `JAILED`."
                ),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # YA ESTÁ JAILED
        # ----------------------------------------------------

        if jailed_role in usuario.roles:
            await ctx.send(
                embed=self.error_embed(
                    f"{usuario.mention} ya está en `JAILED`."
                ),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # GUARDAR ROLES
        # ----------------------------------------------------

        guild_id = str(guild.id)
        user_id = str(usuario.id)

        if guild_id not in self.data:
            self.data[guild_id] = {}

        if user_id in self.data[guild_id]:
            await ctx.send(
                embed=self.error_embed(
                    f"{usuario.mention} ya tiene una sesión de Jail guardada."
                ),
                ephemeral=True
            )
            return

        roles_to_save = []

        for role in usuario.roles:

            # @everyone
            if role.is_default():
                continue

            # Rol gestionado por integración/bot
            if role.managed:
                continue

            # El bot no puede quitarlo
            if role >= bot_member.top_role:
                continue

            roles_to_save.append(role.id)

        # ----------------------------------------------------
        # GUARDAR DATOS
        # ----------------------------------------------------

        self.data[guild_id][user_id] = {
            "roles": roles_to_save,
            "moderator": ctx.author.id,
            "reason": razon
        }

        save_data(self.data)

        # ----------------------------------------------------
        # QUITAR ROLES
        # ----------------------------------------------------

        removed_roles = []

        for role in list(usuario.roles):

            if role.is_default():
                continue

            if role.managed:
                continue

            if role >= bot_member.top_role:
                continue

            try:
                await usuario.remove_roles(
                    role,
                    reason=f"JAILED: {razon}"
                )

                removed_roles.append(role)

            except discord.Forbidden:
                pass

            except discord.HTTPException:
                pass

        # ----------------------------------------------------
        # AÑADIR JAILED
        # ----------------------------------------------------

        try:

            await usuario.add_roles(
                jailed_role,
                reason=f"JAILED: {razon}"
            )

        except discord.Forbidden:

            # Si falla, restaurar los datos
            self.data[guild_id].pop(user_id, None)
            save_data(self.data)

            await ctx.send(
                embed=self.error_embed(
                    "No tengo permisos para ponerle el rol `JAILED`."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException:

            self.data[guild_id].pop(user_id, None)
            save_data(self.data)

            await ctx.send(
                embed=self.error_embed(
                    "Discord rechazó la modificación de roles."
                ),
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🔒 Usuario encarcelado",
            color=discord.Color.dark_red()
        )

        embed.add_field(
            name="👤 Usuario",
            value=f"{usuario.mention}\n`{usuario}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderador",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Razón",
            value=razon,
            inline=False
        )

        embed.add_field(
            name="🎭 Roles guardados",
            value=str(len(roles_to_save)),
            inline=True
        )

        embed.add_field(
            name="🔨 Roles removidos",
            value=str(len(removed_roles)),
            inline=True
        )

        embed.set_thumbnail(url=usuario.display_avatar.url)

        await ctx.send(embed=embed)

    # ========================================================
    # UNJAIL
    # ========================================================

    @commands.hybrid_command(
        name="unjail",
        description="Libera a un usuario de la cárcel."
    )
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def unjail(
        self,
        ctx: commands.Context,
        usuario: discord.Member
    ):

        guild = ctx.guild

        if guild is None:
            return

        guild_id = str(guild.id)
        user_id = str(usuario.id)

        # ----------------------------------------------------
        # DATOS
        # ----------------------------------------------------

        guild_data = self.data.get(guild_id, {})

        jail_data = guild_data.get(user_id)

        if not jail_data:
            await ctx.send(
                embed=self.error_embed(
                    f"No tengo información de Jail para {usuario.mention}."
                ),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # BOT MEMBER
        # ----------------------------------------------------

        bot_member = guild.me

        if bot_member is None:
            bot_member = guild.get_member(self.bot.user.id)

        if bot_member is None:
            await ctx.send(
                embed=self.error_embed(
                    "No pude encontrar mi usuario."
                ),
                ephemeral=True
            )
            return

        # ----------------------------------------------------
        # ROL JAILED
        # ----------------------------------------------------

        jailed_role = discord.utils.get(
            guild.roles,
            name=JAILED_ROLE_NAME
        )

        # ----------------------------------------------------
        # QUITAR JAILED
        # ----------------------------------------------------

        if jailed_role and jailed_role in usuario.roles:

            if jailed_role < bot_member.top_role:

                try:
                    await usuario.remove_roles(
                        jailed_role,
                        reason="UNJAIL"
                    )

                except discord.Forbidden:
                    await ctx.send(
                        embed=self.error_embed(
                            "No tengo permisos para quitar el rol `JAILED`."
                        ),
                        ephemeral=True
                    )
                    return

                except discord.HTTPException:
                    await ctx.send(
                        embed=self.error_embed(
                            "Discord rechazó la modificación de roles."
                        ),
                        ephemeral=True
                    )
                    return

        # ----------------------------------------------------
        # RESTAURAR ROLES
        # ----------------------------------------------------

        restored = 0
        failed = 0

        for role_id in jail_data.get("roles", []):

            role = guild.get_role(role_id)

            if role is None:
                failed += 1
                continue

            if role.is_default():
                continue

            if role.managed:
                failed += 1
                continue

            if role >= bot_member.top_role:
                failed += 1
                continue

            try:

                await usuario.add_roles(
                    role,
                    reason="UNJAIL"
                )

                restored += 1

            except discord.Forbidden:
                failed += 1

            except discord.HTTPException:
                failed += 1

        # ----------------------------------------------------
        # BORRAR DATOS
        # ----------------------------------------------------

        self.data[guild_id].pop(user_id, None)

        if not self.data[guild_id]:
            self.data.pop(guild_id, None)

        save_data(self.data)

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🔓 Usuario liberado",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👤 Usuario",
            value=f"{usuario.mention}\n`{usuario}`",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderador",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="🎭 Roles restaurados",
            value=str(restored),
            inline=True
        )

        if failed:
            embed.add_field(
                name="⚠️ No restaurados",
                value=str(failed),
                inline=True
            )

        embed.set_thumbnail(url=usuario.display_avatar.url)

        await ctx.send(embed=embed)

    # ========================================================
    # LISTA DE JAILED
    # ========================================================

    @commands.hybrid_command(
        name="jailedlist",
        description="Muestra los usuarios actualmente encarcelados."
    )
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def jailedlist(self, ctx: commands.Context):

        guild = ctx.guild

        if guild is None:
            return

        guild_id = str(guild.id)

        guild_data = self.data.get(guild_id, {})

        if not guild_data:
            await ctx.send(
                embed=discord.Embed(
                    title="🔒 Usuarios encarcelados",
                    description="No hay usuarios actualmente encarcelados.",
                    color=discord.Color.dark_red()
                )
            )
            return

        lines = []

        for user_id, info in guild_data.items():

            member = guild.get_member(int(user_id))

            if member:
                name = member.mention
            else:
                name = f"<@{user_id}>"

            reason = info.get(
                "reason",
                "Sin razón"
            )

            lines.append(
                f"🔒 {name} — `{reason}`"
            )

        description = "\n".join(lines)

        if len(description) > 4000:
            description = description[:3990] + "\n..."

        embed = discord.Embed(
            title="🔒 Usuarios encarcelados",
            description=description,
            color=discord.Color.dark_red()
        )

        embed.set_footer(
            text=f"Total: {len(guild_data)}"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    async def cog_command_error(
        self,
        ctx: commands.Context,
        error
    ):

        if isinstance(error, commands.MissingPermissions):

            await ctx.send(
                embed=self.error_embed(
                    "Necesitás el permiso **Moderar miembros** para usar este comando."
                ),
                ephemeral=True
            )

            return

        if isinstance(error, commands.MissingRequiredArgument):

            await ctx.send(
                embed=self.error_embed(
                    "Tenés que especificar un usuario."
                ),
                ephemeral=True
            )

            return

        if isinstance(error, commands.MemberNotFound):

            await ctx.send(
                embed=self.error_embed(
                    "No encontré a ese usuario."
                ),
                ephemeral=True
            )

            return

        if isinstance(error, commands.NoPrivateMessage):

            return

        print(
            f"[JAILED] Error en comando: {error}"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Jailed(bot))