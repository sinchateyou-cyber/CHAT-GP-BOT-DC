import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
CONFIG_FILE = os.path.join(DATA_FOLDER, "config.json")
# ============================================================
# FUNCIONES DE DATOS
# ============================================================
def asegurar_data():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
def cargar_config():
    asegurar_data()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
def guardar_config(config):
    asegurar_data()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            indent=4,
            ensure_ascii=False
        )
def obtener_config(guild_id):
    config = cargar_config()
    guild_id = str(guild_id)
    if guild_id not in config:
        config[guild_id] = {
            "prefijo": "!",
            "color": "5865F2",
            "canales": {
                "bienvenida": None,
                "logs": None
            },
            "roles": {
                "verificado": None,
                "bienvenida": None
            }
        }
        guardar_config(config)
    return config[guild_id]
# ============================================================
# PANEL DE CONFIGURACIÓN
# ============================================================
class ConfiguracionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(
            timeout=300
        )
        self.cog = cog
    # ========================================================
    # VER CONFIGURACIÓN
    # ========================================================
    @discord.ui.button(
        label="Ver configuración",
        emoji="📋",
        style=discord.ButtonStyle.secondary
    )
    async def ver_config(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        config = obtener_config(
            interaction.guild.id
        )
        embed = self.cog.crear_embed_config(
            interaction.guild,
            config
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # RESET
    # ========================================================
    @discord.ui.button(
        label="Restablecer",
        emoji="🔄",
        style=discord.ButtonStyle.danger
    )
    async def reset_config(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás ser administrador.",
                ephemeral=True
            )
            return
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        config[guild_id] = {
            "prefijo": "!",
            "color": "5865F2",
            "canales": {
                "bienvenida": None,
                "logs": None
            },
            "roles": {
                "verificado": None,
                "bienvenida": None
            }
        }
        guardar_config(
            config
        )
        await interaction.response.send_message(
            "✅ La configuración fue restablecida.",
            ephemeral=True
        )
# ============================================================
# COG
# ============================================================
class Configuracion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(
            "[CONFIG] Sistema de configuración cargado."
        )
    # ========================================================
    # GRUPO /CONFIG
    # ========================================================
    config_group = app_commands.Group(
        name="config",
        description="Configurar el servidor y el bot"
    )
    # ========================================================
    # PANEL
    # ========================================================
    @config_group.command(
        name="panel",
        description="Abrir el panel de configuración"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_panel(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="⚙️ Panel de configuración",
            description=(
                "Desde este panel podés consultar "
                "y administrar la configuración del servidor.\n\n"
                "Usá los comandos `/config` para modificar "
                "cada apartado."
            ),
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="📝 Servidor",
            value=(
                "`/config nombre`\n"
                "`/config icono`"
            ),
            inline=True
        )
        embed.add_field(
            name="📢 Canales",
            value=(
                "`/config bienvenida`\n"
                "`/config logs`"
            ),
            inline=True
        )
        embed.add_field(
            name="🎭 Roles",
            value=(
                "`/config rol-verificado`\n"
                "`/config rol-bienvenida`"
            ),
            inline=True
        )
        embed.add_field(
            name="🔧 Bot",
            value=(
                "`/config prefijo`\n"
                "`/config color`"
            ),
            inline=True
        )
        embed.set_footer(
            text="Solo los administradores pueden usar este panel."
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfiguracionView(self),
            ephemeral=True
        )
    # ========================================================
    # NOMBRE
    # ========================================================
    @config_group.command(
        name="nombre",
        description="Cambiar el nombre del servidor"
    )
    @app_commands.describe(
        nombre="Nuevo nombre del servidor"
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def config_nombre(
        self,
        interaction: discord.Interaction,
        nombre: str
    ):
        try:
            await interaction.guild.edit(
                name=nombre
            )
            await interaction.response.send_message(
                f"✅ Nombre cambiado a **{nombre}**.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para cambiar el nombre.",
                ephemeral=True
            )
    # ========================================================
    # ICONO
    # ========================================================
    @config_group.command(
        name="icono",
        description="Cambiar el icono del servidor"
    )
    @app_commands.describe(
        url="URL directa de la imagen"
    )
    @app_commands.checks.has_permissions(
        manage_guild=True
    )
    async def config_icono(
        self,
        interaction: discord.Interaction,
        url: str
    ):
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await interaction.response.send_message(
                            "❌ No pude descargar la imagen.",
                            ephemeral=True
                        )
                        return
                    imagen = await response.read()
            await interaction.guild.edit(
                icon=imagen
            )
            await interaction.response.send_message(
                "✅ Icono del servidor actualizado.",
                ephemeral=True
            )
        except Exception as e:
            print(
                f"[CONFIG] Error icono: {e}"
            )
            await interaction.response.send_message(
                "❌ No pude cambiar el icono.",
                ephemeral=True
            )
    # ========================================================
    # CANAL BIENVENIDA
    # ========================================================
    @config_group.command(
        name="bienvenida",
        description="Configurar el canal de bienvenida"
    )
    @app_commands.describe(
        canal="Canal donde se enviarán las bienvenidas"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_bienvenida(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        if guild_id not in config:
            obtener_config(
                interaction.guild.id
            )
            config = cargar_config()
        config[guild_id][
            "canales"
        ][
            "bienvenida"
        ] = canal.id
        guardar_config(
            config
        )
        await interaction.response.send_message(
            f"✅ Canal de bienvenida configurado: {canal.mention}",
            ephemeral=True
        )
    # ========================================================
    # CANAL LOGS
    # ========================================================
    @config_group.command(
        name="logs",
        description="Configurar el canal de logs"
    )
    @app_commands.describe(
        canal="Canal donde se enviarán los logs"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_logs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        if guild_id not in config:
            obtener_config(
                interaction.guild.id
            )
            config = cargar_config()
        config[guild_id][
            "canales"
        ][
            "logs"
        ] = canal.id
        guardar_config(
            config
        )
        await interaction.response.send_message(
            f"✅ Canal de logs configurado: {canal.mention}",
            ephemeral=True
        )
    # ========================================================
    # ROL VERIFICADO
    # ========================================================
    @config_group.command(
        name="rol-verificado",
        description="Configurar el rol de verificado"
    )
    @app_commands.describe(
        rol="Rol que recibirán los usuarios verificados"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_rol_verificado(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        obtener_config(
            interaction.guild.id
        )
        config = cargar_config()
        config[guild_id][
            "roles"
        ][
            "verificado"
        ] = rol.id
        guardar_config(
            config
        )
        await interaction.response.send_message(
            f"✅ Rol de verificado configurado: {rol.mention}",
            ephemeral=True
        )
    # ========================================================
    # ROL BIENVENIDA
    # ========================================================
    @config_group.command(
        name="rol-bienvenida",
        description="Configurar el rol automático de bienvenida"
    )
    @app_commands.describe(
        rol="Rol que recibirán los nuevos usuarios"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_rol_bienvenida(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        obtener_config(
            interaction.guild.id
        )
        config = cargar_config()
        config[guild_id][
            "roles"
        ][
            "bienvenida"
        ] = rol.id
        guardar_config(
            config
        )
        await interaction.response.send_message(
            f"✅ Rol de bienvenida configurado: {rol.mention}",
            ephemeral=True
        )
    # ========================================================
    # PREFIJO
    # ========================================================
    @config_group.command(
        name="prefijo",
        description="Cambiar el prefijo del bot"
    )
    @app_commands.describe(
        prefijo="Nuevo prefijo"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_prefijo(
        self,
        interaction: discord.Interaction,
        prefijo: str
    ):
        if len(prefijo) > 5:
            await interaction.response.send_message(
                "❌ El prefijo no puede tener más de 5 caracteres.",
                ephemeral=True
            )
            return
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        obtener_config(
            interaction.guild.id
        )
        config = cargar_config()
        config[guild_id][
            "prefijo"
        ] = prefijo
        guardar_config(
            config
        )
        await interaction.response.send_message(
            f"✅ Prefijo cambiado a `{prefijo}`.",
            ephemeral=True
        )
    # ========================================================
    # COLOR
    # ========================================================
    @config_group.command(
        name="color",
        description="Cambiar el color de los embeds"
    )
    @app_commands.describe(
        hexadecimal="Ejemplo: 5865F2"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def config_color(
        self,
        interaction: discord.Interaction,
        hexadecimal: str
    ):
        hexadecimal = hexadecimal.replace(
            "#",
            ""
        )
        try:
            int(
                hexadecimal,
                16
            )
            if len(hexadecimal) != 6:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Color inválido. Usá un formato como `5865F2`.",
                ephemeral=True
            )
            return
        config = cargar_config()
        guild_id = str(
            interaction.guild.id
        )
        obtener_config(
            interaction.guild.id
        )
        config = cargar_config()
        config[guild_id][
            "color"
        ] = hexadecimal.upper()
        guardar_config(
            config
        )
        await interaction.response.send_message(
            f"✅ Color actualizado a `#{hexadecimal.upper()}`.",
            ephemeral=True
        )
    # ========================================================
    # VER CONFIGURACIÓN
    # ========================================================
    def crear_embed_config(
        self,
        guild,
        config
    ):
        embed = discord.Embed(
            title="⚙️ Configuración actual",
            color=discord.Color.blurple()
        )
        canales = config.get(
            "canales",
            {}
        )
        roles = config.get(
            "roles",
            {}
        )
        canal_bienvenida = canales.get(
            "bienvenida"
        )
        canal_logs = canales.get(
            "logs"
        )
        rol_verificado = roles.get(
            "verificado"
        )
        rol_bienvenida = roles.get(
            "bienvenida"
        )
        embed.add_field(
            name="🔧 Prefijo",
            value=f"`{config.get('prefijo', '!')}`",
            inline=True
        )
        embed.add_field(
            name="🎨 Color",
            value=f"`#{config.get('color', '5865F2')}`",
            inline=True
        )
        embed.add_field(
            name="📢 Bienvenida",
            value=(
                f"<#{canal_bienvenida}>"
                if canal_bienvenida
                else "No configurado"
            ),
            inline=True
        )
        embed.add_field(
            name="📜 Logs",
            value=(
                f"<#{canal_logs}>"
                if canal_logs
                else "No configurado"
            ),
            inline=True
        )
        embed.add_field(
            name="🎭 Verificado",
            value=(
                f"<@&{rol_verificado}>"
                if rol_verificado
                else "No configurado"
            ),
            inline=True
        )
        embed.add_field(
            name="👋 Rol bienvenida",
            value=(
                f"<@&{rol_bienvenida}>"
                if rol_bienvenida
                else "No configurado"
            ),
            inline=True
        )
        return embed
    # ========================================================
    # MANEJO DE ERRORES
    # ========================================================
    @config_panel.error
    async def config_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            mensaje = (
                "❌ Necesitás permisos de administrador "
                "para usar este comando."
            )
        else:
            print(
                f"[CONFIG] Error: {error}"
            )
            mensaje = (
                "❌ Ocurrió un error al ejecutar "
                "la configuración."
            )
        if interaction.response.is_done():
            await interaction.followup.send(
                mensaje,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                mensaje,
                ephemeral=True
            )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Configuracion(bot)
    )