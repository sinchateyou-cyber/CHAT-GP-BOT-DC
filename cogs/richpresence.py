import discord
from discord import app_commands
from discord.ext import commands
class RichPresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ============================================================
    # /setpresence
    # ============================================================
    @app_commands.command(
        name="setpresence",
        description="Cambia la actividad que muestra el bot."
    )
    @app_commands.describe(
        tipo="Tipo de actividad que mostrará el bot.",
        texto="Texto que aparecerá en la actividad."
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
                name="🏆 Compitiendo",
                value="compitiendo"
            )
        ]
    )
    @app_commands.default_permissions(administrator=True)
    async def setpresence(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        texto: str
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        if len(texto) > 128:
            await interaction.response.send_message(
                "❌ El texto no puede superar los **128 caracteres**.",
                ephemeral=True
            )
            return
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
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=actividad
        )
        await interaction.response.send_message(
            f"✅ Presencia actualizada.\n"
            f"**Tipo:** {tipo.name}\n"
            f"**Texto:** `{texto}`"
        )
    # ============================================================
    # /clearpresence
    # ============================================================
    @app_commands.command(
        name="clearpresence",
        description="Elimina la actividad actual del bot."
    )
    @app_commands.default_permissions(administrator=True)
    async def clearpresence(
        self,
        interaction: discord.Interaction
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )
            return
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=None
        )
        await interaction.response.send_message(
            "✅ La actividad del bot fue eliminada."
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(RichPresence(bot))