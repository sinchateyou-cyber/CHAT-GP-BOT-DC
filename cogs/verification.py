import discord
from discord.ext import commands
from discord import app_commands
import os
import json

# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "verification.json")

VERIFIED_ROLE_NAME = "Verificado"
VERIFICATION_CHANNEL_NAME = "verificacion"
VERIFICATION_EMOJI = "✅"


# ============================================================
# COG
# ============================================================

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.save_data({})

        self.data = self.load_data()

    # ========================================================
    # DATA
    # ========================================================

    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_data(self, data=None):
        if data is not None:
            self.data = data

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ========================================================
    # OBTENER CONFIGURACIÓN
    # ========================================================

    def get_config(self, guild_id):
        return self.data.get(str(guild_id))

    # ========================================================
    # /SETUPVERIFICACION
    # ========================================================

    @app_commands.command(
        name="setupverificacion",
        description="Crea y configura automáticamente el sistema de verificación."
    )
    async def setup_verificacion(
        self,
        interaction: discord.Interaction
    ):

        # ----------------------------------------------------
        # SERVIDOR
        # ----------------------------------------------------

        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return

        guild = interaction.guild

        # ----------------------------------------------------
        # PERMISOS
        # ----------------------------------------------------

        if interaction.user.id != guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede configurar la verificación.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # ====================================================
        # CREAR / BUSCAR ROL
        # ====================================================

        verified_role = discord.utils.get(
            guild.roles,
            name=VERIFIED_ROLE_NAME
        )

        if verified_role is None:

            try:
                verified_role = await guild.create_role(
                    name=VERIFIED_ROLE_NAME,
                    reason="Sistema automático de verificación"
                )

            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ No tengo permisos para crear el rol `Verificado`.",
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
        # CREAR / BUSCAR CANAL
        # ====================================================

        verification_channel = discord.utils.get(
            guild.text_channels,
            name=VERIFICATION_CHANNEL_NAME
        )

        if verification_channel is None:

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=True,
                    read_message_history=True
                ),

                verified_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=True,
                    read_message_history=True
                )
            }

            try:
                verification_channel = await guild.create_text_channel(
                    VERIFICATION_CHANNEL_NAME,
                    overwrites=overwrites,
                    reason="Sistema automático de verificación"
                )

            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ No tengo permisos para crear el canal.",
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
        # CREAR EMBED
        # ====================================================

        embed = discord.Embed(
            title="🛡️・VERIFICACIÓN",
            description=(
                "Bienvenido a **Band Arg**.\n\n"
                "Para acceder al servidor necesitás verificarte.\n\n"
                f"Reaccioná con {VERIFICATION_EMOJI} debajo de este mensaje "
                "para obtener el rol **Verificado**.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "✅ **Una vez verificado podrás acceder al servidor.**"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text="Sistema automático de verificación"
        )

        # ====================================================
        # ENVIAR MENSAJE
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
                "❌ No tengo permisos para enviar mensajes o agregar reacciones en el canal.",
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

        await interaction.followup.send(
            (
                "✅ **Sistema de verificación creado correctamente.**\n\n"
                f"🛡️ Rol: {verified_role.mention}\n"
                f"📋 Canal: {verification_channel.mention}\n"
                f"🆔 Mensaje: `{message.id}`"
            ),
            ephemeral=True
        )

    # ========================================================
    # /RESETVERIFICACION
    # ========================================================

    @app_commands.command(
        name="resetverificacion",
        description="Elimina la configuración guardada del sistema de verificación."
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
                "⚠️ Este servidor no tiene una configuración de verificación guardada.",
                ephemeral=True
            )
            return

        del self.data[guild_id]
        self.save_data()

        await interaction.response.send_message(
            "✅ La configuración del sistema de verificación fue eliminada.",
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
        # IGNORAR BOTS
        # ----------------------------------------------------

        if payload.user_id == self.bot.user.id:
            return

        # ----------------------------------------------------
        # BUSCAR CONFIGURACIÓN
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

        emoji = payload.emoji

        if emoji.name != config.get("emoji"):
            return

        # ----------------------------------------------------
        # OBTENER GUILD
        # ----------------------------------------------------

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        # ----------------------------------------------------
        # OBTENER USUARIO
        # ----------------------------------------------------

        try:
            member = guild.get_member(payload.user_id)

            if member is None:
                member = await guild.fetch_member(
                    payload.user_id
                )

        except Exception:
            return

        # ----------------------------------------------------
        # OBTENER ROL
        # ----------------------------------------------------

        role = guild.get_role(
            config.get("role_id")
        )

        if role is None:
            return

        # ----------------------------------------------------
        # YA TIENE EL ROL
        # ----------------------------------------------------

        if role in member.roles:
            return

        # ----------------------------------------------------
        # DAR ROL
        # ----------------------------------------------------

        try:

            await member.add_roles(
                role,
                reason="Usuario verificado mediante reacción"
            )

        except discord.Forbidden:
            return

        except Exception:
            return

        # ----------------------------------------------------
        # MENSAJE PRIVADO
        # ----------------------------------------------------

        try:

            await member.send(
                f"✅ **Te verificaste correctamente en {guild.name}.**\n"
                f"Se te otorgó el rol **{role.name}**."
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
        # IGNORAR BOTS
        # ----------------------------------------------------

        if payload.user_id == self.bot.user.id:
            return

        # ----------------------------------------------------
        # BUSCAR CONFIG
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

        guild = self.bot.get_guild(
            payload.guild_id
        )

        if guild is None:
            return

        # ----------------------------------------------------
        # MEMBER
        # ----------------------------------------------------

        member = guild.get_member(
            payload.user_id
        )

        if member is None:
            return

        # ----------------------------------------------------
        # ROLE
        # ----------------------------------------------------

        role = guild.get_role(
            config.get("role_id")
        )

        if role is None:
            return

        # ----------------------------------------------------
        # QUITAR ROL
        # ----------------------------------------------------

        if role not in member.roles:
            return

        try:

            await member.remove_roles(
                role,
                reason="Usuario quitó la reacción de verificación"
            )

        except discord.Forbidden:
            pass

        except Exception:
            pass


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(
        Verification(bot)
    )