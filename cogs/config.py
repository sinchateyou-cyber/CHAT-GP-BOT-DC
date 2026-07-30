import os
import json
import discord
from discord import app_commands
from discord.ext import commands

# ============================================================
# ARCHIVO DE CONFIGURACIÓN
# ============================================================

CONFIG_FILE = "data/server_config.json"


# ============================================================
# FUNCIONES DE CONFIGURACIÓN
# ============================================================

def ensure_data_folder():
    """Crea la carpeta data si no existe."""
    os.makedirs("data", exist_ok=True)


def load_config():
    """Carga la configuración de todos los servidores."""
    ensure_data_folder()

    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if not isinstance(data, dict):
                return {}

            return data

    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config):
    """Guarda la configuración de todos los servidores."""
    ensure_data_folder()

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)


def get_server_config(guild_id):
    """Obtiene la configuración de un servidor."""
    config = load_config()
    guild_id = str(guild_id)

    if guild_id not in config:
        config[guild_id] = {
            "welcome_channel": None,
            "log_channel": None,
            "welcome_enabled": False,
            "logs_enabled": False
        }
        save_config(config)

    return config[guild_id]


def update_server_config(guild_id, key, value):
    """Actualiza una configuración específica."""
    config = load_config()
    guild_id = str(guild_id)

    if guild_id not in config:
        config[guild_id] = {
            "welcome_channel": None,
            "log_channel": None,
            "welcome_enabled": False,
            "logs_enabled": False
        }

    config[guild_id][key] = value
    save_config(config)


# ============================================================
# COG CONFIG
# ============================================================

class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        ensure_data_folder()

    # ========================================================
    # /config
    # ========================================================

    config_group = app_commands.Group(
        name="config",
        description="Configura las opciones del servidor."
    )

    # ========================================================
    # /config ver
    # ========================================================

    @config_group.command(
        name="ver",
        description="Muestra la configuración actual del servidor."
    )
    @app_commands.guild_only()
    async def config_ver(self, interaction: discord.Interaction):

        guild = interaction.guild
        settings = get_server_config(guild.id)

        welcome_channel_id = settings.get("welcome_channel")
        log_channel_id = settings.get("log_channel")

        welcome_channel = (
            guild.get_channel(welcome_channel_id)
            if welcome_channel_id
            else None
        )

        log_channel = (
            guild.get_channel(log_channel_id)
            if log_channel_id
            else None
        )

        embed = discord.Embed(
            title="⚙️ Configuración del servidor",
            description=f"Configuración de **{guild.name}**",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="👋 Bienvenidas",
            value=(
                "🟢 Activadas"
                if settings.get("welcome_enabled", False)
                else "🔴 Desactivadas"
            ),
            inline=True
        )

        embed.add_field(
            name="📜 Logs",
            value=(
                "🟢 Activados"
                if settings.get("logs_enabled", False)
                else "🔴 Desactivados"
            ),
            inline=True
        )

        embed.add_field(
            name="📢 Canal de bienvenida",
            value=welcome_channel.mention if welcome_channel else "No configurado",
            inline=False
        )

        embed.add_field(
            name="📋 Canal de logs",
            value=log_channel.mention if log_channel else "No configurado",
            inline=False
        )

        embed.set_footer(
            text=f"Servidor ID: {guild.id}"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /config bienvenida
    # ========================================================

    @config_group.command(
        name="bienvenida",
        description="Configura el canal de bienvenida."
    )
    @app_commands.describe(
        canal="Canal donde se enviarán las bienvenidas."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def config_bienvenida(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        update_server_config(
            interaction.guild.id,
            "welcome_channel",
            canal.id
        )

        update_server_config(
            interaction.guild.id,
            "welcome_enabled",
            True
        )

        embed = discord.Embed(
            title="✅ Bienvenidas configuradas",
            description=(
                f"Las bienvenidas se enviarán ahora en {canal.mention}."
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /config logs
    # ========================================================

    @config_group.command(
        name="logs",
        description="Configura el canal de logs."
    )
    @app_commands.describe(
        canal="Canal donde se enviarán los logs."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def config_logs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        update_server_config(
            interaction.guild.id,
            "log_channel",
            canal.id
        )

        update_server_config(
            interaction.guild.id,
            "logs_enabled",
            True
        )

        embed = discord.Embed(
            title="✅ Logs configurados",
            description=(
                f"Los logs se enviarán ahora en {canal.mention}."
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /config desactivar-bienvenida
    # ========================================================

    @config_group.command(
        name="desactivar-bienvenida",
        description="Desactiva el sistema de bienvenida."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def desactivar_bienvenida(
        self,
        interaction: discord.Interaction
    ):

        update_server_config(
            interaction.guild.id,
            "welcome_enabled",
            False
        )

        embed = discord.Embed(
            title="🔴 Bienvenidas desactivadas",
            description="El sistema de bienvenida fue desactivado.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /config desactivar-logs
    # ========================================================

    @config_group.command(
        name="desactivar-logs",
        description="Desactiva el sistema de logs."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def desactivar_logs(
        self,
        interaction: discord.Interaction
    ):

        update_server_config(
            interaction.guild.id,
            "logs_enabled",
            False
        )

        embed = discord.Embed(
            title="🔴 Logs desactivados",
            description="El sistema de logs fue desactivado.",
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Config(bot))