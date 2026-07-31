import os
import asyncio
import threading

import discord
from discord.ext import commands
from flask import Flask


app = Flask(__name__)


@app.route("/")
def home():
    return "Bot online"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port
    )


TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1529314985174368438


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True


class MiBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):

        extensiones = [
            "cogs.lock",
            "cogs.avatar",
            "cogs.antilink",
            "cogs.antiflood",
            "cogs.antispam",
            "cogs.owner",
            "cogs.ban",
            "cogs.kick",
            "cogs.timeout",
            "cogs.untimeout",
            "cogs.unlock",
            "cogs.afk",
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.tickets",
            "cogs.verification",
            "cogs.utilidades",
            "cogs.canales",
            "cogs.say",
            "cogs.nick",
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            "cogs.setstatus",
            "cogs.invite",
            "cogs.help",
            "cogs.clear",
            "cogs.addemoji",
            "cogs.invites",
            "cogs.invites_command",
            "cogs.invites_leaderboard",
            "cogs.botinfo",
            "cogs.config",
            "cogs.play",
            "cogs.stop",
            "cogs.leave",
            "cogs.server_setup"
        ]

        for extension in extensiones:
            try:
                await self.load_extension(extension)
                print(f"✅ Cargado: {extension}")

            except Exception as error:
                print(
                    f"❌ Error en {extension}: {error}"
                )

        guild = discord.Object(
            id=GUILD_ID
        )

        try:

            self.tree.copy_global_to(
                guild=guild
            )

            synced = await self.tree.sync(
                guild=guild
            )

            print(
                f"✅ Slash Commands sincronizados: "
                f"{len(synced)}"
            )

        except Exception as error:

            print(
                f"❌ Error sincronizando comandos: "
                f"{error}"
            )


bot = MiBot()


@bot.event
async def on_ready():

    print("=" * 40)

    print(
        f"🤖 Bot conectado: {bot.user}"
    )

    print(
        f"🆔 ID: {bot.user.id}"
    )

    print(
        f"🌐 Servidores: {len(bot.guilds)}"
    )

    print("=" * 40)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/help 💎"
        )
    )


async def main():

    if not TOKEN:

        print(
            "❌ ERROR: No existe la variable "
            "DISCORD_TOKEN"
        )

        return

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    await bot.start(
        TOKEN
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )