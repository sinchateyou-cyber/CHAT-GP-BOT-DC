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
# FUNCIONES PARA MANEJAR LA CONFIGURACIÓN
# ============================================================

def load_config():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_config(data):
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_guild_config(guild_id):
    data = load_config()
    guild_id = str(guild_id)

    if guild_id not in data:
        data[guild_id] = {
            "logs_channel": None,
            "welcome_channel": None,
            "autorole": None,
            "prefix": "!"
        }
        save_config(data)

    return data[guild_id]


# ============================================================
# COG
# ============================================================

class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # GRUPO /CONFIG
    # ========================================================

    config_group = app_commands.Group(
        name="config",
        description="Configura el bot para este servidor."
    )

    # ========================================================
    # /CONFIG SHOW
    # ========================================================

    @config_group.command(
        name="show",
        description="Muestra la configuración actual del servidor."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_show(self, interaction: discord.Interaction):

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo puede usarse dentro de un servidor.",
                ephemeral=True
            )

        config = get_guild_config(interaction.guild.id)

        # Canal de logs
        logs_channel = "No configurado"

        if config["logs_channel"]:
            channel = interaction.guild.get_channel(
                config["logs_channel"]
            )

            if channel:
                logs_channel = channel.mention

        # Canal de bienvenida
        welcome_channel = "No configurado"

        if config["welcome_channel"]:
            channel = interaction.guild.get_channel(
                config["welcome_channel"]
            )

            if channel:
                welcome_channel = channel.mention

        # Autorol
        autorole = "No configurado"

        if config["autorole"]:
            role = interaction.guild.get_role(
                config["autorole"]
            )

            if role:
                autorole = role.mention

        embed = discord.Embed(
            title="⚙️ Configuración del servidor",
            description=f"Configuración de **{interaction.guild.name}**",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📜 Canal de logs",
            value=logs_channel,
            inline=False
        )

        embed.add_field(
            name="👋 Canal de bienvenida",
            value=welcome_channel,
            inline=False
        )

        embed.add_field(
            name="🎭 Autorol",
            value=autorole,
            inline=False
        )

        embed.add_field(
            name="⌨️ Prefijo",
            value=f"`{config['prefix']}`",
            inline=False
        )

        embed.set_footer(
            text=f"Servidor ID: {interaction.guild.id}"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONFIG LOGS
    # ========================================================

    @config_group.command(
        name="logs",
        description="Configura el canal donde se enviarán los logs."
    )
    @app_commands.describe(
        canal="Canal donde se enviarán los logs."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_logs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(interaction.guild.id)

        data[guild_id]["logs_channel"] = canal.id

        save_config(data)

        embed = discord.Embed(
            title="✅ Canal de logs configurado",
            description=f"Los logs se enviarán en {canal.mention}.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONFIG WELCOME
    # ========================================================

    @config_group.command(
        name="welcome",
        description="Configura el canal de bienvenida."
    )
    @app_commands.describe(
        canal="Canal donde se enviarán las bienvenidas."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_welcome(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(interaction.guild.id)

        data[guild_id]["welcome_channel"] = canal.id

        save_config(data)

        embed = discord.Embed(
            title="✅ Bienvenida configurada",
            description=f"Las bienvenidas se enviarán en {canal.mention}.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONFIG AUTOROLE
    # ========================================================

    @config_group.command(
        name="autorole",
        description="Configura el rol automático para nuevos miembros."
    )
    @app_commands.describe(
        rol="Rol que recibirán los nuevos miembros."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_autorole(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(interaction.guild.id)

        data[guild_id]["autorole"] = rol.id

        save_config(data)

        embed = discord.Embed(
            title="✅ Autorol configurado",
            description=f"Los nuevos miembros recibirán {rol.mention}.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONFIG PREFIX
    # ========================================================

    @config_group.command(
        name="prefix",
        description="Configura el prefijo del bot."
    )
    @app_commands.describe(
        prefijo="Nuevo prefijo del bot. Ejemplo: !"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_prefix(
        self,
        interaction: discord.Interaction,
        prefijo: str
    ):

        if len(prefijo) > 5:
            return await interaction.response.send_message(
                "❌ El prefijo no puede tener más de 5 caracteres.",
                ephemeral=True
            )

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(interaction.guild.id)

        data[guild_id]["prefix"] = prefijo

        save_config(data)

        embed = discord.Embed(
            title="✅ Prefijo configurado",
            description=f"El nuevo prefijo es `{prefijo}`.",
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONFIG RESET
    # ========================================================

    @config_group.command(
        name="reset",
        description="Restablece toda la configuración del servidor."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_reset(
        self,
        interaction: discord.Interaction
    ):

        data = load_config()
        guild_id = str(interaction.guild.id)

        data[guild_id] = {
            "logs_channel": None,
            "welcome_channel": None,
            "autorole": None,
            "prefix": "!"
        }

        save_config(data)

        embed = discord.Embed(
            title="♻️ Configuración restablecida",
            description="Toda la configuración de este servidor volvió a sus valores predeterminados.",
            color=discord.Color.orange()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# MANEJO DE ERRORES
# ============================================================

async def config_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):
        await interaction.response.send_message(
            "❌ Necesitás permisos de **Administrador** para usar este comando.",
            ephemeral=True
        )

    else:
        print(
            f"Error en /config: {error}"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Config(bot))