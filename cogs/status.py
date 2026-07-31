import discord
from discord import app_commands
from discord.ext import commands
class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ============================================================
    # /setstatus
    # Cambia el estado del bot
    # ============================================================
    @app_commands.command(
        name="setstatus",
        description="Cambia el estado del bot."
    )
    @app_commands.describe(
        estado="Seleccioná el estado del bot."
    )
    @app_commands.choices(
        estado=[
            app_commands.Choice(
                name="🟢 Online",
                value="online"
            ),
            app_commands.Choice(
                name="🟡 Ausente",
                value="idle"
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
    @app_commands.default_permissions(
        administrator=True
    )
    async def setstatus(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        # ========================================================
        # COMPROBAR PERMISOS
        # ========================================================
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        # ========================================================
        # CONVERTIR ESTADO
        # ========================================================
        estados = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        nuevo_estado = estados.get(
            estado.value
        )
        if nuevo_estado is None:
            await interaction.response.send_message(
                "❌ Estado inválido.",
                ephemeral=True
            )
            return
        # ========================================================
        # CAMBIAR ESTADO
        # ========================================================
        await self.bot.change_presence(
            status=nuevo_estado
        )
        await interaction.response.send_message(
            f"✅ Estado del bot cambiado a "
            f"**{estado.name}**."
        )
    # ============================================================
    # /setactivity
    # Cambia la actividad del bot
    # ============================================================
    @app_commands.command(
        name="setactivity",
        description="Cambia la actividad del bot."
    )
    @app_commands.describe(
        tipo="Seleccioná el tipo de actividad.",
        texto="Escribí el texto de la actividad."
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(
                name="🎮 Jugando",
                value="playing"
            ),
            app_commands.Choice(
                name="👀 Viendo",
                value="watching"
            ),
            app_commands.Choice(
                name="🎧 Escuchando",
                value="listening"
            ),
            app_commands.Choice(
                name="🏆 Compitiendo",
                value="competing"
            )
        ]
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def setactivity(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        texto: str
    ):
        # ========================================================
        # COMPROBAR PERMISOS
        # ========================================================
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        # ========================================================
        # LÍMITE DE TEXTO
        # ========================================================
        if len(texto) > 128:
            await interaction.response.send_message(
                "❌ El texto no puede superar los **128 caracteres**.",
                ephemeral=True
            )
            return
        # ========================================================
        # CREAR ACTIVIDAD
        # ========================================================
        if tipo.value == "playing":
            actividad = discord.Game(
                name=texto
            )
        elif tipo.value == "watching":
            actividad = discord.Activity(
                type=discord.ActivityType.watching,
                name=texto
            )
        elif tipo.value == "listening":
            actividad = discord.Activity(
                type=discord.ActivityType.listening,
                name=texto
            )
        elif tipo.value == "competing":
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
        # ========================================================
        # CAMBIAR ACTIVIDAD
        # ========================================================
        await self.bot.change_presence(
            activity=actividad
        )
        await interaction.response.send_message(
            f"✅ Actividad actualizada.\n\n"
            f"**Tipo:** {tipo.name}\n"
            f"**Texto:** `{texto}`"
        )
    # ============================================================
    # /clearactivity
    # Elimina la actividad
    # ============================================================
    @app_commands.command(
        name="clearactivity",
        description="Elimina la actividad actual del bot."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def clearactivity(
        self,
        interaction: discord.Interaction
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        await self.bot.change_presence(
            activity=None
        )
        await interaction.response.send_message(
            "✅ Actividad eliminada correctamente."
        )
    # ============================================================
    # /clearstatus
    # Restablece el estado
    # ============================================================
    @app_commands.command(
        name="clearstatus",
        description="Restablece el estado del bot a Online."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def clearstatus(
        self,
        interaction: discord.Interaction
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        await self.bot.change_presence(
            status=discord.Status.online
        )
        await interaction.response.send_message(
            "✅ El bot volvió a estar **🟢 Online**."
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Status(bot)
    )