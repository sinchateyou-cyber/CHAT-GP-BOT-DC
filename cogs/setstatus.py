import discord
from discord import app_commands
from discord.ext import commands


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setstatus",
        description="Cambia el estado del bot."
    )
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Jugando", value="playing"),
        app_commands.Choice(name="Escuchando", value="listening"),
        app_commands.Choice(name="Viendo", value="watching"),
        app_commands.Choice(name="Compitiendo", value="competing"),
    ])
    async def setstatus(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        texto: str
    ):
        if tipo.value == "playing":
            actividad = discord.Game(name=texto)

        elif tipo.value == "listening":
            actividad = discord.Activity(
                type=discord.ActivityType.listening,
                name=texto
            )

        elif tipo.value == "watching":
            actividad = discord.Activity(
                type=discord.ActivityType.watching,
                name=texto
            )

        elif tipo.value == "competing":
            actividad = discord.Activity(
                type=discord.ActivityType.competing,
                name=texto
            )

        await self.bot.change_presence(activity=actividad)

        await interaction.response.send_message(
            f"✅ Estado cambiado a: **{texto}**"
        )


async def setup(bot):
    await bot.add_cog(Status(bot))