import os
import asyncio
import threading

import discord
from discord.ext import commands
from flask import Flask


# ============================================================
# SERVIDOR WEB PARA RENDER
# ============================================================

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


# ============================================================
# TOKEN
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.voice_states = True


# ============================================================
# BOT
# ============================================================

class MiBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    # ========================================================
    # CARGAR COGS
    # ========================================================

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

            "cogs.server_setup",
            "cogs.levels",
            "cogs.xp"
        ]


        # ====================================================
        # CARGAR EXTENSIONES
        # ====================================================

        for extension in extensiones:

            try:

                await self.load_extension(
                    extension
                )

                print(
                    f"✅ COG CARGADO: {extension}"
                )

            except Exception as error:

                print(
                    f"❌ ERROR CARGANDO: "
                    f"{extension}"
                )

                print(
                    f"   {type(error).__name__}: "
                    f"{error}"
                )


        # ====================================================
        # MOSTRAR COMANDOS
        # ====================================================

        print("")
        print("========================================")
        print("📋 COMANDOS REGISTRADOS")
        print("========================================")

        comandos = self.tree.get_commands()

        for comando in comandos:

            print(
                f"✅ /{comando.name}"
            )

        print(
            f"TOTAL: {len(comandos)}"
        )

        print("========================================")
        print("")


        # ====================================================
        # SINCRONIZACIÓN GLOBAL
        # ====================================================

        try:

            print(
                "🌎 Sincronizando comandos globalmente..."
            )

            synced = await self.tree.sync()

            print(
                "✅ SINCRONIZACIÓN COMPLETADA"
            )

            print(
                f"🌎 Comandos globales: {len(synced)}"
            )

            print("")

        except Exception as error:

            print(
                "❌ ERROR EN SINCRONIZACIÓN GLOBAL"
            )

            print(
                f"{type(error).__name__}: {error}"
            )


# ============================================================
# CREAR BOT
# ============================================================

bot = MiBot()


# ============================================================
# BOT LISTO
# ============================================================

@bot.event
async def on_ready():

    print("")
    print("========================================")
    print("🤖 BOT ONLINE")
    print("========================================")

    print(
        f"Nombre: {bot.user}"
    )

    print(
        f"ID: {bot.user.id}"
    )

    print(
        f"Servidores: {len(bot.guilds)}"
    )

    print(
        f"Comandos: {len(bot.tree.get_commands())}"
    )

    print("========================================")
    print("")


    # ========================================================
    # ESTADO DEL BOT
    # ========================================================

    await bot.change_presence(

        activity=discord.Activity(

            type=discord.ActivityType.watching,

            name="/help 💎"
        )
    )


# ============================================================
# INICIAR BOT
# ============================================================

async def main():

    # ========================================================
    # COMPROBAR TOKEN
    # ========================================================

    if not TOKEN:

        print(
            "❌ ERROR: DISCORD_TOKEN NO ESTÁ CONFIGURADO"
        )

        return


    # ========================================================
    # SERVIDOR WEB
    # ========================================================

    threading.Thread(

        target=run_web,

        daemon=True

    ).start()


    # ========================================================
    # INICIAR DISCORD
    # ========================================================

    try:

        await bot.start(
            TOKEN
        )

    except Exception as error:

        print(
            "❌ ERROR INICIANDO BOT:"
        )

        print(
            f"{type(error).__name__}: {error}"
        )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )