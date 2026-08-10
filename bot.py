import os
import asyncio
import threading
import secrets
import json
import traceback
from urllib.parse import urlencode

import discord
from discord.ext import commands

from flask import (
    Flask,
    jsonify,
    render_template,
    redirect,
    request,
    session
)

import requests


# ============================================================
# CONFIGURACIÓN
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI",
    "https://TU-APP.onrender.com/callback"
)

OWNER_ID = 1004206704994566164


# ============================================================
# INTENTS
# ============================================================

intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.voice_states = True
intents.presences = True


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

    async def setup_hook(self):

        cogs = [
            "cogs.moderation",
            "cogs.antilink",
            "cogs.antiflood",
            "cogs.antispam",
            "cogs.afk",
            "cogs.avatar",
            "cogs.nick",
            "cogs.utilidades",
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            "cogs.canales",
            "cogs.reglas",
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.logs_salidas",
            "cogs.tickets",
            "cogs.verification",
            "cogs.server_setup",
            "cogs.say",
            "cogs.help",
            "cogs.owner",
            "cogs.invites",
            "cogs.botinfo",
            "cogs.config",
            "cogs.dashboard",
            "cogs.addemoji",
            "cogs.social",
            "cogs.key",
            "cogs.status",
            "cogs.xp",
            "cogs.reactionroles",
            "cogs.configuracionall",
            "cogs.interacciones",
            "cogs.mute",
        ]

        for cog in cogs:

            try:
                await self.load_extension(cog)
                print(f"✅ Cog cargado: {cog}")

            except Exception as e:

                print(f"❌ Error cargando {cog}: {e}")
                traceback.print_exc()

        # ====================================================
        # SINCRONIZAR SLASH COMMANDS
        # ====================================================

        try:

            synced = await self.tree.sync()

            print(
                f"✅ {len(synced)} comandos slash sincronizados."
            )

        except Exception as e:

            print(
                f"❌ Error sincronizando comandos: {e}"
            )

    async def on_ready(self):

        print("=" * 50)
        print(f"🤖 Bot conectado como {self.user}")
        print(f"🆔 ID: {self.user.id}")
        print(f"🌐 Servidores: {len(self.guilds)}")
        print("=" * 50)


bot = MiBot()


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32)
)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return """
    <!DOCTYPE html>
    <html lang="es">

    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Bot Dashboard</title>

        <style>

            body {
                margin: 0;
                background: #080808;
                color: white;
                font-family: Arial, sans-serif;

                display: flex;
                justify-content: center;
                align-items: center;

                min-height: 100vh;
            }

            .box {
                background: #111;
                border: 1px solid #6f00ff;
                border-radius: 20px;

                padding: 40px;

                width: 90%;
                max-width: 600px;

                text-align: center;

                box-shadow:
                    0 0 30px rgba(128, 0, 255, .25);
            }

            h1 {
                color: #a855f7;
            }

            p {
                color: #aaa;
            }

        </style>

    </head>

    <body>

        <div class="box">

            <h1>🤖 Bot Dashboard</h1>

            <p>
                El bot está funcionando correctamente.
            </p>

        </div>

    </body>

    </html>
    """


# ============================================================
# API STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    return jsonify({

        "online": bot.is_ready(),

        "bot": str(bot.user)
        if bot.user else None,

        "guilds": len(bot.guilds),

        "latency": round(
            bot.latency * 1000
        )
        if bot.is_ready()
        else None

    })


# ============================================================
# DISCORD LOGIN
# ============================================================

@app.route("/login")
def login():

    params = {

        "client_id": DISCORD_CLIENT_ID,

        "redirect_uri": DISCORD_REDIRECT_URI,

        "response_type": "code",

        "scope": "identify guilds"

    }

    url = (
        "https://discord.com/oauth2/authorize?"
        + urlencode(params)
    )

    return redirect(url)


# ============================================================
# CALLBACK
# ============================================================

@app.route("/callback")
def callback():

    code = request.args.get("code")

    if not code:
        return "No se recibió código.", 400

    data = {

        "client_id": DISCORD_CLIENT_ID,

        "client_secret": DISCORD_CLIENT_SECRET,

        "grant_type": "authorization_code",

        "code": code,

        "redirect_uri": DISCORD_REDIRECT_URI

    }

    headers = {
        "Content-Type":
            "application/x-www-form-urlencoded"
    }

    response = requests.post(
        "https://discord.com/api/oauth2/token",
        data=data,
        headers=headers
    )

    if response.status_code != 200:

        return (
            "Error obteniendo el token de Discord.",
            500
        )

    token_data = response.json()

    access_token = token_data.get(
        "access_token"
    )

    user_response = requests.get(
        "https://discord.com/api/users/@me",
        headers={
            "Authorization":
                f"Bearer {access_token}"
        }
    )

    if user_response.status_code != 200:

        return (
            "Error obteniendo usuario.",
            500
        )

    user = user_response.json()

    session["user"] = user

    return redirect("/dashboard")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    user = session.get("user")

    if not user:
        return redirect("/login")

    return f"""
    <!DOCTYPE html>

    <html lang="es">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Dashboard</title>

        <style>

            body {{
                margin: 0;
                background: #080808;
                color: white;
                font-family: Arial;
            }}

            .container {{
                max-width: 1000px;
                margin: auto;
                padding: 40px;
            }}

            .card {{
                background: #111;
                border: 1px solid #6f00ff;
                border-radius: 20px;
                padding: 25px;
                margin-top: 20px;
            }}

            h1 {{
                color: #a855f7;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>
                Bienvenido, {user.get("username")}
            </h1>

            <div class="card">

                <h2>🤖 Estado del bot</h2>

                <p>
                    Online: {bot.is_ready()}
                </p>

                <p>
                    Servidores: {len(bot.guilds)}
                </p>

                <p>
                    Latencia:
                    {round(bot.latency * 1000)
                    if bot.is_ready() else 0} ms
                </p>

            </div>

        </div>

    </body>

    </html>
    """


# ============================================================
# RUN FLASK
# ============================================================

def run_flask():

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    if not TOKEN:

        raise RuntimeError(
            "❌ Falta la variable DISCORD_TOKEN."
        )

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    await bot.start(TOKEN)


if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("Bot detenido.")

    except Exception:

        traceback.print_exc()