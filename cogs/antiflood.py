import discord
from discord.ext import commands
from discord import app_commands
from collections import defaultdict, deque
import time


class AntiFlood(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = defaultdict(bool)
        self.messages = defaultdict(lambda: deque(maxlen=10))

    @app_commands.command(
        name="antiflood",
        description="Activa o desactiva el sistema anti-flood."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.choices(estado=[
        app_commands.Choice(name="Activar", value="on"),
        app_commands.Choice(name="Desactivar", value="off")
    ])
    async def antiflood(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        self.config[interaction.guild.id] = estado.value == "on"

        if estado.value == "on":
            await interaction.response.send_message(
                "🌊 **Anti-Flood activado correctamente.**"
            )
        else:
            await interaction.response.send_message(
                "🔴 **Anti-Flood desactivado correctamente.**"
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot or not message.guild:
            return

        if not self.config.get(message.guild.id, False):
            return

        usuario = message.author
        ahora = time.time()

        mensajes = self.messages[
            (message.guild.id, usuario.id)
        ]

        mensajes.append(ahora)

        # 8 mensajes en 3 segundos = flood
        recientes = [
            tiempo for tiempo in mensajes
            if ahora - tiempo <= 3
        ]

        if len(recientes) >= 8:

            try:
                await message.delete()

                await message.channel.send(
                    f"🌊 {usuario.mention}, **no hagas flood en el servidor.**",
                    delete_after=5
                )

                mensajes.clear()

            except discord.Forbidden:
                pass


async def setup(bot):
    await bot.add_cog(AntiFlood(bot))