import discord
from discord import app_commands
from discord.ext import commands
class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ============================================================
    # CONVERTIR TEXTO A ESTADO DE DISCORD
    # ============================================================
    def get_status(self, estado: str):
        estados = {
            "online": discord.Status.online,
            "ausente": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        return estados.get(estado)
    # ============================================================
    # /setstatus
    # Cambia el estado del bot
    # ============================================================
    @app_commands.command(
        name="setstatus",
        description="Cambia el estado del bot."
    )
    @app_commands.describe(
        estado="Selecciona el estado que tendrá el bot."
    )
    @app_commands.choices(
        estado=[
            app_commands.Choice(
                name="🟢 Online",
                value="online"
            ),
            app_commands.Choice(
                name="🟡 Ausente",
                value="ausente"
            ),
            app_commands.Choice(
                name="🔴 No molestar",
                value="dnd"
            ),
            app_commands.Choice(
                name="⚫ Invisible",
                value="invisible"
            )
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def setstatus(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        # Comprobar permisos
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        nuevo_estado = self.get_status(estado.value)
        if nuevo_estado is None:
            await interaction.response.send_message(
                "❌ El estado seleccionado no es válido.",
                ephemeral=True
            )
            return
        # Cambiar estado manteniendo la actividad actual
        await self.bot.change_presence(
            status=nuevo_estado
        )
        await interaction.response.send_message(
            f"✅ Estado del bot cambiado a **{estado.name}**."
        )
    # ============================================================
    # /setactivity
    # Cambia la actividad del bot
    # ============================================================
    @app_commands.command(
        name="setactivity",
        description="Cambia la actividad que muestra el bot."
    )
    @app_commands.describe(
        tipo="Selecciona el tipo de actividad.",
        texto="Escribe el texto que aparecerá."
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(
                name="🎮 Jugando",
                value="jugando"
            ),
            app_commands.Choice(
                name="🎧 Escuchando",
                value="escuchando"
            ),
            app_commands.Choice(
                name="👀 Viendo",
                value="viendo"
            ),
            app_commands.Choice(
                name="📺 Transmitiendo",
                value="transmitiendo"
            ),
            app_commands.Choice(
                name="🏆 Compitiendo",
                value="compitiendo"
            )
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def setactivity(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        texto: str
    ):
        # Comprobar permisos
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        # Limitar texto
        if len(texto) > 128:
            await interaction.response.send_message(
                "❌ El texto no puede superar los **128 caracteres**.",
                ephemeral=True
            )
            return
        # Crear actividad
        if tipo.value == "jugando":
            actividad = discord.Game(
                name=texto
            )
        elif tipo.value == "escuchando":
            actividad = discord.Activity(
                type=discord.ActivityType.listening,
                name=texto
            )
        elif tipo.value == "viendo":
            actividad = discord.Activity(
                type=discord.ActivityType.watching,
                name=texto
            )
        elif tipo.value == "transmitiendo":
            actividad = discord.Streaming(
                name=texto,
                url="https://www.twitch.tv/"
            )
        elif tipo.value == "compitiendo":
            actividad = discord.Activity(
                type=discord.ActivityType.competing,
                name=texto
            )
        else:
            await interaction.response.send_message(
                "❌ Tipo de actividad inválido.",
                ephemeral=True
            )
            return
        # Cambiar actividad manteniendo el estado actual
        await self.bot.change_presence(
            activity=actividad
        )
        await interaction.response.send_message(
            f"✅ Actividad actualizada correctamente.\n\n"
            f"**Tipo:** {tipo.name}\n"
            f"**Texto:** `{texto}`"
        )
    # ============================================================
    # /clearactivity
    # Elimina solamente la actividad
    # ============================================================
    @app_commands.command(
        name="clearactivity",
        description="Elimina la actividad actual del bot."
    )
    @app_commands.default_permissions(administrator=True)
    async def clearactivity(
        self,
        interaction: discord.Interaction
    ):
        # Comprobar permisos
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        # Quitar actividad
        await self.bot.change_presence(
            activity=None
        )
        await interaction.response.send_message(
            "✅ La actividad del bot fue eliminada."
        )
    # ============================================================
    # /clearstatus
    # Restablece estado y actividad
    # ============================================================
    @app_commands.command(
        name="clearstatus",
        description="Restablece el estado y la actividad del bot."
    )
    @app_commands.default_permissions(administrator=True)
    async def clearstatus(
        self,
        interaction: discord.Interaction
    ):
        # Comprobar permisos
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        # Restablecer todo
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=None
        )
        await interaction.response.send_message(
            "✅ El estado del bot fue restablecido.\n"
            "🟢 Estado: **Online**\n"
            "🧹 Actividad: **Ninguna**"
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Status(bot)
    )