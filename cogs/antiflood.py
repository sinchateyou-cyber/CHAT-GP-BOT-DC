import os
import json
import time
import discord
from collections import defaultdict, deque
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
# ANTI-FLOOD
# ============================================================
class AntiFlood(commands.Cog):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        self.config = load_config()
        self.messages = defaultdict(
            lambda: deque(
                maxlen=10
            )
        )
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
            "antiflood",
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
            "antiflood"
        ] = enabled
        save_config(
            self.config
        )
    # ========================================================
    # COMANDO /ANTIFLOOD
    # ========================================================
    @app_commands.command(
        name="antiflood",
        description="Activa o desactiva el sistema anti-flood."
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
    async def antiflood(
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
                "🌊 **Anti-Flood activado correctamente.**"
            )
        else:
            await interaction.response.send_message(
                "🔴 **Anti-Flood desactivado correctamente.**"
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
        usuario = message.author
        ahora = time.time()
        mensajes = self.messages[
            (
                message.guild.id,
                usuario.id
            )
        ]
        mensajes.append(
            ahora
        )
        # ====================================================
        # 8 MENSAJES EN 3 SEGUNDOS
        # ====================================================
        recientes = [
            tiempo
            for tiempo in mensajes
            if ahora - tiempo <= 3
        ]
        if len(
            recientes
        ) >= 8:
            try:
                await message.delete()
                await message.channel.send(
                    f"🌊 {usuario.mention}, **no hagas flood en el servidor.**",
                    delete_after=5
                )
                mensajes.clear()
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
        AntiFlood(
            bot
        )
    )