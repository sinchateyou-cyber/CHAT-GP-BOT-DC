import discord
from discord import app_commands
from discord.ext import commands
class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # /setstatus
    # =========================
    @app_commands.command(
        name="setstatus",
        description="Cambia el estado del bot"
    )
    @app_commands.describe(
        texto="Texto que mostrará el bot",
        tipo="Tipo de estado"
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(name="Jugando", value="playing"),
            app_commands.Choice(name="Escuchando", value="listening"),
            app_commands.Choice(name="Viendo", value="watching"),
            app_commands.Choice(name="Compitiendo", value="competing"),
        ]
    )
    async def setstatus(
        self,
        interaction: discord.Interaction,
        texto: str,
        tipo: app_commands.Choice[str]
    ):
        tipos = {
            "playing": discord.ActivityType.playing,
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching,
            "competing": discord.ActivityType.competing
        }
        actividad = discord.Activity(
            type=tipos[tipo.value],
            name=texto
        )
        await self.bot.change_presence(activity=actividad)
        await interaction.response.send_message(
            f"✅ Estado cambiado a: **{tipo.name} {texto}**",
            ephemeral=True
        )
    # =========================
    # /clearstatus
    # =========================
    @app_commands.command(
        name="clearstatus",
        description="Elimina el estado actual del bot"
    )
    async def clearstatus(self, interaction: discord.Interaction):
        await self.bot.change_presence(activity=None)
        await interaction.response.send_message(
            "✅ Estado eliminado correctamente.",
            ephemeral=True
        )
async def setup(bot):
    await bot.add_cog(Status(bot))

Comandos

/setstatus texto: Mi servidor tipo: Jugando

/setstatus texto: música tipo: Escuchando

/setstatus texto: Discord tipo: Viendo

/clearstatus

Guardalo como:

cogs/status.py

Y asegurate de cargar el cog desde tu bot.py.

:::
Si querés, también puedo hacerlo con **`/status`**, donde el bot te muestre un menú para elegir el tipo de estado y cambiarlo desde un solo comando.