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

def load_config():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_config(data):
    os.makedirs("data", exist_ok=True)

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


def reset_guild_config(guild_id):
    data = load_config()

    data[str(guild_id)] = {
        "logs_channel": None,
        "welcome_channel": None,
        "autorole": None,
        "prefix": "!"
    }

    save_config(data)


# ============================================================
# EMBED PRINCIPAL
# ============================================================

def create_config_embed(guild, config):
    logs = "No configurado"
    welcome = "No configurado"
    autorole = "No configurado"

    if config.get("logs_channel"):
        channel = guild.get_channel(config["logs_channel"])
        if channel:
            logs = channel.mention

    if config.get("welcome_channel"):
        channel = guild.get_channel(config["welcome_channel"])
        if channel:
            welcome = channel.mention

    if config.get("autorole"):
        role = guild.get_role(config["autorole"])
        if role:
            autorole = role.mention

    embed = discord.Embed(
        title="⚙️ Configuración del servidor",
        description=(
            f"Configurá **{guild.name}** usando el menú de abajo.\n\n"
            "Seleccioná una opción para modificar la configuración."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📜 Logs",
        value=logs,
        inline=False
    )

    embed.add_field(
        name="👋 Bienvenida",
        value=welcome,
        inline=False
    )

    embed.add_field(
        name="🎭 Autorol",
        value=autorole,
        inline=False
    )

    embed.add_field(
        name="⌨️ Prefijo",
        value=f"`{config.get('prefix', '!')}`",
        inline=False
    )

    embed.set_footer(
        text=f"Servidor ID: {guild.id}"
    )

    return embed


# ============================================================
# MODAL PARA CONFIGURAR PREFIJO
# ============================================================

class PrefixModal(discord.ui.Modal, title="⌨️ Configurar prefijo"):

    prefijo = discord.ui.TextInput(
        label="Nuevo prefijo",
        placeholder="Ejemplo: !",
        min_length=1,
        max_length=5,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(interaction.guild.id)

        data[guild_id]["prefix"] = str(self.prefijo.value)

        save_config(data)

        await interaction.response.send_message(
            f"✅ El prefijo del servidor ahora es `{self.prefijo.value}`.",
            ephemeral=True
        )


# ============================================================
# SELECT DE CONFIGURACIÓN
# ============================================================

class ConfigSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Configurar logs",
                description="Elegí el canal donde se enviarán los logs.",
                emoji="📜",
                value="logs"
            ),
            discord.SelectOption(
                label="Configurar bienvenida",
                description="Elegí el canal para los mensajes de bienvenida.",
                emoji="👋",
                value="welcome"
            ),
            discord.SelectOption(
                label="Configurar autorol",
                description="Elegí el rol automático para nuevos miembros.",
                emoji="🎭",
                value="autorole"
            ),
            discord.SelectOption(
                label="Configurar prefijo",
                description="Cambiá el prefijo de los comandos tradicionales.",
                emoji="⌨️",
                value="prefix"
            ),
            discord.SelectOption(
                label="Actualizar panel",
                description="Actualizá la información de configuración.",
                emoji="🔄",
                value="refresh"
            ),
            discord.SelectOption(
                label="Restablecer configuración",
                description="Volvé toda la configuración a los valores predeterminados.",
                emoji="♻️",
                value="reset"
            )
        ]

        super().__init__(
            placeholder="⚙️ Seleccioná una opción...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="config_select"
        )

    async def callback(self, interaction: discord.Interaction):

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ Este menú solo puede usarse dentro de un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )

        opcion = self.values[0]

        # ====================================================
        # LOGS
        # ====================================================

        if opcion == "logs":

            canales = [
                channel
                for channel in interaction.guild.text_channels
            ]

            if not canales:
                return await interaction.response.send_message(
                    "❌ No hay canales de texto disponibles.",
                    ephemeral=True
                )

            view = ChannelSelectView(
                mode="logs",
                channels=canales
            )

            await interaction.response.send_message(
                "📜 **Seleccioná el canal donde se enviarán los logs:**",
                view=view,
                ephemeral=True
            )

        # ====================================================
        # WELCOME
        # ====================================================

        elif opcion == "welcome":

            canales = [
                channel
                for channel in interaction.guild.text_channels
            ]

            if not canales:
                return await interaction.response.send_message(
                    "❌ No hay canales de texto disponibles.",
                    ephemeral=True
                )

            view = ChannelSelectView(
                mode="welcome",
                channels=canales
            )

            await interaction.response.send_message(
                "👋 **Seleccioná el canal de bienvenida:**",
                view=view,
                ephemeral=True
            )

        # ====================================================
        # AUTOROLE
        # ====================================================

        elif opcion == "autorole":

            roles = [
                role
                for role in interaction.guild.roles
                if role != interaction.guild.default_role
                and not role.managed
            ]

            if not roles:
                return await interaction.response.send_message(
                    "❌ No hay roles disponibles.",
                    ephemeral=True
                )

            view = RoleSelectView(roles)

            await interaction.response.send_message(
                "🎭 **Seleccioná el rol automático:**",
                view=view,
                ephemeral=True
            )

        # ====================================================
        # PREFIX
        # ====================================================

        elif opcion == "prefix":

            await interaction.response.send_modal(
                PrefixModal()
            )

        # ====================================================
        # REFRESH
        # ====================================================

        elif opcion == "refresh":

            config = get_guild_config(
                interaction.guild.id
            )

            embed = create_config_embed(
                interaction.guild,
                config
            )

            await interaction.response.edit_message(
                embed=embed
            )

        # ====================================================
        # RESET
        # ====================================================

        elif opcion == "reset":

            reset_guild_config(
                interaction.guild.id
            )

            config = get_guild_config(
                interaction.guild.id
            )

            embed = create_config_embed(
                interaction.guild,
                config
            )

            await interaction.response.edit_message(
                embed=embed
            )

            await interaction.followup.send(
                "♻️ La configuración del servidor fue restablecida.",
                ephemeral=True
            )


# ============================================================
# SELECT DE CANALES
# ============================================================

class ChannelSelect(discord.ui.Select):

    def __init__(self, mode, channels):

        self.mode = mode

        options = []

        for channel in channels[:25]:

            options.append(
                discord.SelectOption(
                    label=channel.name[:100],
                    description=f"ID: {channel.id}",
                    value=str(channel.id),
                    emoji="📁"
                )
            )

        super().__init__(
            placeholder="📁 Seleccioná un canal...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ Este menú solo puede usarse en un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )

        channel_id = int(self.values[0])

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(
            interaction.guild.id
        )

        if self.mode == "logs":

            data[guild_id]["logs_channel"] = channel_id

            save_config(data)

            channel = interaction.guild.get_channel(
                channel_id
            )

            await interaction.response.send_message(
                f"✅ Canal de logs configurado en {channel.mention}.",
                ephemeral=True
            )

        elif self.mode == "welcome":

            data[guild_id]["welcome_channel"] = channel_id

            save_config(data)

            channel = interaction.guild.get_channel(
                channel_id
            )

            await interaction.response.send_message(
                f"✅ Canal de bienvenida configurado en {channel.mention}.",
                ephemeral=True
            )


class ChannelSelectView(discord.ui.View):

    def __init__(self, mode, channels):

        super().__init__(
            timeout=60
        )

        self.add_item(
            ChannelSelect(
                mode,
                channels
            )
        )


# ============================================================
# SELECT DE ROLES
# ============================================================

class RoleSelect(discord.ui.Select):

    def __init__(self, roles):

        options = []

        for role in roles[:25]:

            options.append(
                discord.SelectOption(
                    label=role.name[:100],
                    description=f"ID: {role.id}",
                    value=str(role.id),
                    emoji="🎭"
                )
            )

        super().__init__(
            placeholder="🎭 Seleccioná un rol...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ Este menú solo puede usarse en un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )

        role_id = int(self.values[0])

        data = load_config()
        guild_id = str(interaction.guild.id)

        get_guild_config(
            interaction.guild.id
        )

        data[guild_id]["autorole"] = role_id

        save_config(data)

        role = interaction.guild.get_role(
            role_id
        )

        await interaction.response.send_message(
            f"✅ Autorol configurado: {role.mention}.",
            ephemeral=True
        )


class RoleSelectView(discord.ui.View):

    def __init__(self, roles):

        super().__init__(
            timeout=60
        )

        self.add_item(
            RoleSelect(roles)
        )


# ============================================================
# VIEW PRINCIPAL
# ============================================================

class ConfigView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=300
        )

        self.add_item(
            ConfigSelect()
        )


# ============================================================
# COG
# ============================================================

class Config(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ========================================================
    # /CONFIG SERVER
    # ========================================================

    config_group = app_commands.Group(
        name="config",
        description="Configura el bot para este servidor."
    )

    @config_group.command(
        name="server",
        description="Abre el panel de configuración del servidor."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_server(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo puede usarse dentro de un servidor.",
                ephemeral=True
            )

        config = get_guild_config(
            interaction.guild.id
        )

        embed = create_config_embed(
            interaction.guild,
            config
        )

        await interaction.response.send_message(
            embed=embed,
            view=ConfigView(),
            ephemeral=True
        )


# ============================================================
# ERROR HANDLER
# ============================================================

async def config_server_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )

    else:

        print(
            f"❌ Error en /config server: {error}"
        )

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ Ocurrió un error al ejecutar la configuración.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Ocurrió un error al ejecutar la configuración.",
                ephemeral=True
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Config(bot)
    )