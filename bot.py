import os
import asyncio
import threading

import discord
from discord.ext import commands
from flask import Flask


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

GUILD_ID = 1534290216418938891


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot online", 200


def run_web():
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True


# ============================================================
# BOT
# ============================================================

class MiBot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="s!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):

        print("========================================")
        print("📦 SETUP")
        print("========================================")

        guild = discord.Object(
            id=GUILD_ID
        )

        try:

            synced = await self.tree.sync(
                guild=guild
            )

            print(
                f"✅ SLASH REGISTRADOS: {len(synced)}"
            )

            for command in synced:
                print(
                    f"   /{command.name}"
                )

        except Exception as error:

            print(
                "❌ ERROR SYNC:"
            )

            print(
                type(error).__name__,
                error
            )


bot = MiBot()


# ============================================================
# TEST
# ============================================================

@bot.hybrid_command(
    name="test",
    description="Comprueba si el bot funciona."
)
async def test(ctx):

    await ctx.send(
        "✅ El bot funciona correctamente."
    )


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    print("")
    print("========================================")
    print("🟢 BOT READY")
    print("========================================")

    print(
        f"🤖 Usuario: {bot.user}"
    )

    print(
        f"🆔 ID: {bot.user.id}"
    )

    print(
        f"🌐 Servidores: {len(bot.guilds)}"
    )

    print(
        f"📡 Ping: {round(bot.latency * 1000)} ms"
    )

    print("========================================")


# ============================================================
# ERROR SLASH
# ============================================================

@bot.tree.error
async def slash_error(
    interaction,
    error
):

    print(
        "❌ ERROR SLASH:",
        type(error).__name__,
        error
    )

    try:

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ Error ejecutando el comando.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Error ejecutando el comando.",
                ephemeral=True
            )

    except Exception:
        pass


# ============================================================
# ERROR PREFIX
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    print(
        "❌ ERROR PREFIX:",
        type(error).__name__,
        error
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("")
    print("========================================")
    print("🚀 INICIANDO BOT")
    print("========================================")

    if not TOKEN:

        print(
            "❌ NO EXISTE DISCORD_TOKEN"
        )

        return

    print(
        "🔑 TOKEN ENCONTRADO"
    )

    print(
        f"📦 discord.py: {discord.__version__}"
    )

    # Flask
    try:

        thread = threading.Thread(
            target=run_web,
            daemon=True
        )

        thread.start()

        print(
            f"🌐 Flask iniciado en puerto {PORT}"
        )

    except Exception as error:

        print(
            "❌ Error Flask:",
            error
        )

    # Discord
    try:

        print(
            "🔵 CONECTANDO A DISCORD..."
        )

        await bot.start(
            TOKEN
        )

    except discord.LoginFailure:

        print(
            "❌ TOKEN DE DISCORD INVÁLIDO"
        )

    except discord.PrivilegedIntentsRequired:

        print(
            "❌ FALTAN INTENTS PRIVILEGIADOS"
        )

        print(
            "Activá Message Content Intent, "
            "Server Members Intent y "
            "Presence Intent en Discord Developer Portal."
        )

    except Exception as error:

        print(
            "❌ ERROR FATAL:"
        )

        print(
            type(error).__name__,
            error
        )

        import traceback

        traceback.print_exc()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    try:

        asyncio.run(
            main()
        )

    except Exception as error:

        print(
            "❌ ERROR PRINCIPAL:"
        )

        print(
            type(error).__name__,
            error
        )