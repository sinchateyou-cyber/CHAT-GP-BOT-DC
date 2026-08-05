import discord
from discord.ext import commands
from discord import app_commands
import json
import os


FILE = "data/status.json"


def load_status():

    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({}, f, indent=4)

    with open(FILE, "r") as f:
        return json.load(f)



def save_status(data):

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)



class Status(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    async def apply_status(self):

        data = load_status()

        config = data.get(
            "status"
        )

        if not config:
            return


        texto = config.get(
            "text",
            "Usa /help"
        )

        tipo = config.get(
            "type",
            "playing"
        )

        estado = config.get(
            "status",
            "online"
        )


        activity = None


        if tipo == "playing":

            activity = discord.Game(
                name=texto
            )


        elif tipo == "listening":

            activity = discord.Activity(
                type=discord.ActivityType.listening,
                name=texto
            )


        elif tipo == "watching":

            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=texto
            )


        elif tipo == "streaming":

            activity = discord.Streaming(
                name=texto,
                url="https://twitch.tv/"
            )



        status_map = {

            "online":
                discord.Status.online,

            "idle":
                discord.Status.idle,

            "dnd":
                discord.Status.dnd,

            "offline":
                discord.Status.invisible
        }



        await self.bot.change_presence(
            status=status_map.get(
                estado,
                discord.Status.online
            ),
            activity=activity
        )




    @commands.Cog.listener()
    async def on_ready(self):

        await self.apply_status()

        print(
            "🟣 Status personalizado cargado."
        )




    @app_commands.command(
        name="setstatus",
        description="Cambia el estado del bot"
    )
    @app_commands.describe(
        texto="Texto del estado",
        tipo="playing/listening/watching/streaming",
        estado="online/idle/dnd"
    )
    async def setstatus(
        self,
        interaction: discord.Interaction,
        texto: str,
        tipo: str = "playing",
        estado: str = "online"
    ):


        data = load_status()


        data["status"] = {

            "text":
                texto,

            "type":
                tipo.lower(),

            "status":
                estado.lower()
        }


        save_status(data)


        await self.bot.change_presence(
            activity=discord.Game(
                name=texto
            )
        )


        await interaction.response.send_message(
            f"✅ Estado cambiado:\n"
            f"🎮 Tipo: `{tipo}`\n"
            f"📝 Texto: `{texto}`\n"
            f"🟢 Estado: `{estado}`",
            ephemeral=True
        )



    @app_commands.command(
        name="clearstatus",
        description="Quita el estado personalizado"
    )
    async def clearstatus(
        self,
        interaction: discord.Interaction
    ):

        data = load_status()

        data.pop(
            "status",
            None
        )

        save_status(data)


        await self.bot.change_presence(
            activity=None,
            status=discord.Status.online
        )


        await interaction.response.send_message(
            "🗑️ Estado eliminado.",
            ephemeral=True
        )



async def setup(bot):

    await bot.add_cog(
        Status(bot)
    )