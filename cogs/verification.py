import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio

# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "verification.json")

VERIFIED_ROLE_NAME = "Verificado"
VERIFICATION_CHANNEL_NAME = "verificacion"
VERIFICATION_EMOJI = "✅"


# ============================================================
# COG VERIFICATION
# ============================================================

class Verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.save_data({})

        self.data = self.load_data()

    # ========================================================
    # CARGAR DATOS
    # ========================================================

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, dict):
                    return data

                return {}

        except (FileNotFoundError, json.JSONDecodeError):
            return {}

        except Exception as e:
            print(f"[VERIFICATION] Error cargando datos: {e}")
            return {}

    # ========================================================
    # GUARDAR DATOS
    # ========================================================

    def save_data(self, data=None):

        if data is not None:
            self.data = data

        try:
            os.makedirs(DATA_FOLDER, exist_ok=True)

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    self.data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:
            print(f"[VERIFICATION] Error guardando datos: {e}")

    # ========================================================
    # CONFIG DE SERVIDOR
    # ========================================================

    def get_config(self, guild_id):

        return self.data.get(str(guild_id))

    # ========================================================
    # VALIDAR PANEL AL INICIAR
    # ========================================================

    async def validate_saved_panels(self):

        await self.bot.wait_until_ready()

        print("[VERIFICATION] Comprobando paneles guardados...")

        for guild_id, config in list(self.data.items()):

            try:

                guild = self.bot.get_guild(int(guild_id))

                if guild is None:
                    continue

                channel_id = config.get("channel_id")
                message_id = config.get("message_id")
                role_id = config.get("role_id")

                if not channel_id or not message_id or not role_id:
                    print(
                        f"[VERIFICATION] Configuración inválida en {guild.name}"
                    )
                    continue

                channel = guild.get_channel(channel_id)

                if channel is None:
                    try:
                        channel = await guild.fetch_channel(channel_id)
                    except Exception:
                        print(
                            f"[VERIFICATION] No pude encontrar "
                            f"el canal de verificación de {guild.name}"
                        )
                        continue

                role = guild.get_role(role_id)

                if role is None:
                    print(
                        f"[VERIFICATION] No pude encontrar "
                        f"el rol Verificado de {guild.name}"
                    )
                    continue

                try:

                    message = await channel.fetch_message(message_id)

                    print(
                        f"[VERIFICATION] Panel activo: "
                        f"{guild.name} | mensaje {message.id}"
                    )

                except discord.NotFound:

                    print(
                        f"[VERIFICATION] El panel de {guild.name} "
                        f"ya no existe."
                    )

                except discord.Forbidden:

                    print(
                        f"[VERIFICATION] No tengo permiso para "
                        f"ver el panel de {guild.name}."
                    )

                except Exception as e:

                    print(
                        f"[VERIFICATION] Error comprobando "
                        f"{guild.name}: {e}"
                    )

            except Exception as e:

                print(
                    f"[VERIFICATION] Error comprobando servidor "
                    f"{guild_id}: {e}"
                )

    # ========================================================
    # PERMISOS DE CANALES
    # ========================================================

    async def configure_channel_permissions(
        self,
        channel,
        guild,
        verified_role,
        is_verification=False
    ):

        everyone = guild.default_role

        if is_verification:

            await channel.set_permissions(
                everyone,
                view_channel=True,
                send_messages=False,
                read_message_history=True,
                add_reactions=True,
                reason="Canal de verificación"
            )

            await channel.set_permissions(
                verified_role,
                view_channel=True,
                send_messages=False,
                read_message_history=True,
                add_reactions=True,
                reason="Rol verificado"
            )

        else:

            await channel.set_permissions(
                everyone,
                view_channel=False,
                reason="Bloqueo de usuarios no verificados"
            )

            await channel.set_permissions(
                verified_role,
                view_channel=True,
                reason="Acceso para usuarios verificados"
            )

    # ========================================================
    # /SETUPVERIFICACION
    # ========================================================

    @app_commands.command(
        name="setupverificacion",
        description="Configura automáticamente el sistema de verificación."
    )
    async def setup_verificacion(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return

        guild = interaction.guild

        # ----------------------------------------------------
        # SOLO OWNER
        # ----------------------------------------------------

        if interaction.user.id != guild.owner_id:

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede configurar la verificación.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # ====================================================
        # ROL VERIFICADO
        # ====================================================

        verified_role = discord.utils.get(
            guild.roles,
            name=VERIFIED_ROLE_NAME
        )

        if verified_role is None:

            try:

                verified_role = await guild.create_role(
                    name=VERIFIED_ROLE_NAME,
                    reason="Sistema de verificación"
                )

            except discord.Forbidden:

                await interaction.followup.send(
                    "❌ No tengo permiso para crear roles.",
                    ephemeral=True
                )
                return

            except Exception as e:

                await interaction.followup.send(
                    f"❌ Error creando el rol:\n`{e}`",
                    ephemeral=True
                )
                return

        # ====================================================
        # CANAL DE VERIFICACIÓN
        # ====================================================

        verification_channel = discord.utils.get(
            guild.text_channels,
            name=VERIFICATION_CHANNEL_NAME
        )

        if verification_channel is None:

            try:

                verification_channel = await guild.create_text_channel(
                    VERIFICATION_CHANNEL_NAME,
                    reason="Sistema de verificación"
                )

            except discord.Forbidden:

                await interaction.followup.send(
                    "❌ No tengo permiso para crear canales.",
                    ephemeral=True
                )
                return

            except Exception as e:

                await interaction.followup.send(
                    f"❌ Error creando el canal:\n`{e}`",
                    ephemeral=True
                )
                return

        # ====================================================
        # PERMISOS CANAL VERIFICACIÓN
        # ====================================================

        try:

            await self.configure_channel_permissions(
                verification_channel,
                guild,
                verified_role,
                True
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ No tengo permisos para configurar el canal de verificación.",
                ephemeral=True
            )
            return

        except Exception as e:

            await interaction.followup.send(
                f"❌ Error configurando el canal:\n`{e}`",
                ephemeral=True
            )
            return

        # ====================================================
        # BLOQUEAR CANALES NORMALES
        # ====================================================

        failed_channels = []

        for channel in guild.channels:

            if channel.id == verification_channel.id:
                continue

            if isinstance(channel, discord.CategoryChannel):
                continue

            try:

                await self.configure_channel_permissions(
                    channel,
                    guild,
                    verified_role,
                    False
                )

            except discord.Forbidden:

                failed_channels.append(channel.name)

            except Exception:

                failed_channels.append(channel.name)

        # ====================================================
        # CONFIGURAR CATEGORÍAS
        # ====================================================

        for category in guild.categories:

            contains_verification = any(
                c.id == verification_channel.id
                for c in category.channels
            )

            if contains_verification:
                continue

            try:

                await category.set_permissions(
                    guild.default_role,
                    view_channel=False,
                    reason="Bloqueo de usuarios no verificados"
                )

                await category.set_permissions(
                    verified_role,
                    view_channel=True,
                    reason="Acceso para usuarios verificados"
                )

            except discord.Forbidden:

                failed_channels.append(category.name)

            except Exception:

                failed_channels.append(category.name)

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="🛡️・VERIFICACIÓN",
            description=(
                "Bienvenido a **Band Arg**.\n\n"
                "Para acceder al servidor necesitás verificarte.\n\n"
                f"Reaccioná con {VERIFICATION_EMOJI} "
                "para obtener el rol **Verificado**.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "✅ **Una vez verificado se desbloquearán "
                "los canales del servidor.**"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text="Sistema automático de verificación"
        )

        # ====================================================
        # BORRAR PANEL ANTERIOR
        # ====================================================

        old_config = self.get_config(guild.id)

        if old_config:

            old_message_id = old_config.get("message_id")

            if old_message_id:

                try:

                    old_message = await verification_channel.fetch_message(
                        old_message_id
                    )

                    await old_message.delete()

                except discord.NotFound:
                    pass

                except discord.Forbidden:
                    pass

                except Exception:
                    pass

        # ====================================================
        # ENVIAR PANEL
        # ====================================================

        try:

            message = await verification_channel.send(
                embed=embed
            )

            await message.add_reaction(
                VERIFICATION_EMOJI
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ No tengo permisos para enviar el panel o agregar reacciones.",
                ephemeral=True
            )
            return

        except Exception as e:

            await interaction.followup.send(
                f"❌ Error enviando el panel:\n`{e}`",
                ephemeral=True
            )
            return

        # ====================================================
        # GUARDAR CONFIGURACIÓN
        # ====================================================

        self.data[str(guild.id)] = {
            "role_id": verified_role.id,
            "channel_id": verification_channel.id,
            "message_id": message.id,
            "emoji": VERIFICATION_EMOJI
        }

        self.save_data()

        # ====================================================
        # RESPUESTA
        # ====================================================

        texto = (
            "✅ **Sistema de verificación configurado.**\n\n"
            f"🛡️ Rol: {verified_role.mention}\n"
            f"📋 Canal: {verification_channel.mention}\n\n"
            "🔒 Los usuarios no verificados solo podrán "
            "ver el canal de verificación.\n"
            "✅ Al reaccionar recibirán el rol y se "
            "desbloquearán los canales.\n\n"
            "💾 **El panel queda guardado y seguirá "
            "funcionando después de reiniciar el bot.**"
        )

        if failed_channels:

            texto += (
                "\n\n⚠️ **No pude modificar algunos canales:**\n"
                + ", ".join(
                    f"`{name}`"
                    for name in failed_channels[:15]
                )
            )

        await interaction.followup.send(
            texto,
            ephemeral=True
        )

    # ========================================================
    # /RESETVERIFICACION
    # ========================================================

    @app_commands.command(
        name="resetverificacion",
        description="Elimina la configuración guardada de verificación."
    )
    async def reset_verificacion(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return

        guild = interaction.guild

        if interaction.user.id != guild.owner_id:

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede utilizar este comando.",
                ephemeral=True
            )
            return

        guild_id = str(guild.id)

        if guild_id not in self.data:

            await interaction.response.send_message(
                "⚠️ No hay configuración de verificación guardada.",
                ephemeral=True
            )
            return

        del self.data[guild_id]

        self.save_data()

        await interaction.response.send_message(
            "✅ Se eliminó la configuración guardada de verificación.",
            ephemeral=True
        )

    # ========================================================
    # REACCIÓN AGREGADA
    # ========================================================

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent
    ):

        # ----------------------------------------------------
        # IGNORAR BOT
        # ----------------------------------------------------

        if self.bot.user and payload.user_id == self.bot.user.id:
            return

        # ----------------------------------------------------
        # IGNORAR DMS
        # ----------------------------------------------------

        if payload.guild_id is None:
            return

        # ----------------------------------------------------
        # BUSCAR CONFIG
        # ----------------------------------------------------

        config = self.get_config(payload.guild_id)

        if not config:
            return

        # ----------------------------------------------------
        # COMPROBAR MENSAJE
        # ----------------------------------------------------

        if payload.message_id != config.get("message_id"):
            return

        # ----------------------------------------------------
        # COMPROBAR EMOJI
        # ----------------------------------------------------

        if payload.emoji.name != config.get("emoji"):
            return

        # ----------------------------------------------------
        # GUILD
        # ----------------------------------------------------

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:

            try:
                guild = await self.bot.fetch_guild(payload.guild_id)
            except Exception:
                return

        # ----------------------------------------------------
        # MEMBER
        # ----------------------------------------------------

        member = guild.get_member(payload.user_id)

        if member is None:

            try:

                member = await guild.fetch_member(
                    payload.user_id
                )

            except discord.NotFound:
                return

            except discord.Forbidden:
                return

            except Exception:
                return

        # ----------------------------------------------------
        # ROL
        # ----------------------------------------------------

        role_id = config.get("role_id")

        if not role_id:
            return

        role = guild.get_role(role_id)

        if role is None:
            return

        # ----------------------------------------------------
        # YA VERIFICADO
        # ----------------------------------------------------

        if role in member.roles:
            return

        # ----------------------------------------------------
        # DAR ROL
        # ----------------------------------------------------

        try:

            await member.add_roles(
                role,
                reason="Verificación mediante reacción"
            )

            print(
                f"[VERIFICATION] {member} "
                f"se verificó en {guild.name}"
            )

        except discord.Forbidden:

            print(
                f"[VERIFICATION] No tengo permisos "
                f"para dar el rol a {member}"
            )
            return

        except Exception as e:

            print(
                f"[VERIFICATION] Error dando rol: {e}"
            )
            return

        # ----------------------------------------------------
        # MENSAJE PRIVADO
        # ----------------------------------------------------

        try:

            await member.send(
                f"✅ **Te verificaste correctamente en {guild.name}.**\n\n"
                "Ahora tenés acceso a los canales del servidor."
            )

        except Exception:
            pass

    # ========================================================
    # REACCIÓN ELIMINADA
    # ========================================================

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload: discord.RawReactionActionEvent
    ):

        # ----------------------------------------------------
        # IGNORAR BOT
        # ----------------------------------------------------

        if self.bot.user and payload.user_id == self.bot.user.id:
            return

        # ----------------------------------------------------
        # IGNORAR DMS
        # ----------------------------------------------------

        if payload.guild_id is None:
            return

        # ----------------------------------------------------
        # CONFIG
        # ----------------------------------------------------

        config = self.get_config(payload.guild_id)

        if not config:
            return

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        if payload.message_id != config.get("message_id"):
            return

        # ----------------------------------------------------
        # EMOJI
        # ----------------------------------------------------

        if payload.emoji.name != config.get("emoji"):
            return

        # ----------------------------------------------------
        # GUILD
        # ----------------------------------------------------

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        # ----------------------------------------------------
        # MEMBER
        # ----------------------------------------------------

        member = guild.get_member(payload.user_id)

        if member is None:

            try:

                member = await guild.fetch_member(
                    payload.user_id
                )

            except Exception:
                return

        # ----------------------------------------------------
        # ROLE
        # ----------------------------------------------------

        role_id = config.get("role_id")

        if not role_id:
            return

        role = guild.get_role(role_id)

        if role is None:
            return

        # ----------------------------------------------------
        # SI NO TIENE EL ROL
        # ----------------------------------------------------

        if role not in member.roles:
            return

        # ----------------------------------------------------
        # QUITAR ROL
        # ----------------------------------------------------

        try:

            await member.remove_roles(
                role,
                reason="Se quitó la reacción de verificación"
            )

            print(
                f"[VERIFICATION] Se quitó Verificado "
                f"a {member} en {guild.name}"
            )

        except discord.Forbidden:

            print(
                f"[VERIFICATION] No tengo permisos "
                f"para quitar el rol a {member}"
            )

        except Exception as e:

            print(
                f"[VERIFICATION] Error quitando rol: {e}"
            )

    # ========================================================
    # EVENTO DE READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        # Evitar que se ejecute varias veces
        if getattr(self, "_validated", False):
            return

        self._validated = True

        await self.validate_saved_panels()


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Verification(bot)
    )