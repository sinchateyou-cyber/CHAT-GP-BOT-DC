import os
import json
import discord
import re
from discord.ext import commands
from discord import app_commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
CONFIG_FILE = "data/security.json"
# ============================================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================================
def ensure_data_folder():
    if not os.path.exists("data"):
        os.makedirs("data")
def load_config():
    ensure_data_folder()
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except Exception as error:
        print(
            f"❌ Error leyendo security.json: {error}"
        )
        return {}
def save_config(config):
    ensure_data_folder()
    try:
        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                config,
                file,
                indent=4,
                ensure_ascii=False
            )
    except Exception as error:
        print(
            f"❌ Error guardando security.json: {error}"
        )
# ============================================================
# ANTI-LINK
# ============================================================
class AntiLink(commands.Cog):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        self.config = load_config()
    # ========================================================
    # OBTENER ESTADO
    # ========================================================
    def is_enabled(
        self,
        guild_id
    ):
        guild_config = self.config.get(
            str(guild_id),
            {}
        )
        return guild_config.get(
            "antilink",
            False
        )
    # ========================================================
    # CAMBIAR ESTADO
    # ========================================================
    def set_enabled(
        self,
        guild_id,
        enabled
    ):
        guild_id = str(
            guild_id
        )
        if guild_id not in self.config:
            self.config[guild_id] = {}
        self.config[guild_id][
            "antilink"
        ] = enabled
        save_config(
            self.config
        )
    # ========================================================
    # COMANDO /ANTILINK
    # ========================================================
    @app_commands.command(
        name="antilink",
        description="Activa o desactiva el sistema anti-links."
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    @app_commands.choices(
        estado=[
            app_commands.Choice(
                name="Activar",
                value="on"
            ),
            app_commands.Choice(
                name="Desactivar",
                value="off"
            )
        ]
    )
    async def antilink(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        enabled = (
            estado.value == "on"
        )
        self.set_enabled(
            interaction.guild.id,
            enabled
        )
        if enabled:
            await interaction.response.send_message(
                "🛡️ **Anti-Link activado correctamente.**"
            )
        else:
            await interaction.response.send_message(
                "🔴 **Anti-Link desactivado correctamente.**"
            )
    # ========================================================
    # EVENTO DE MENSAJES
    # ========================================================
    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):
        if (
            message.author.bot
            or not message.guild
        ):
            return
        if not self.is_enabled(
            message.guild.id
        ):
            return
        # ====================================================
        # PERMITIR A MODERADORES
        # ====================================================
        if message.author.guild_permissions.manage_messages:
            return
        # ====================================================
        # DETECTAR LINKS
        # ====================================================
        patron = (
            r"(https?://\S+|"
            r"www\.\S+|"
            r"discord\.gg/\S+)"
        )
        if re.search(
            patron,
            message.content,
            re.IGNORECASE
        ):
            try:
                await message.delete()
                await message.channel.send(
                    f"🔗 {message.author.mention}, **no se permiten links en este servidor.**",
                    delete_after=5
                )
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot
):
    await bot.add_cog(
        AntiLink(
            bot
        )
    )