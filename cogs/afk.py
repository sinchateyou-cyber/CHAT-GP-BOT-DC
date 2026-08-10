import os
import json
from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "afk.json")

os.makedirs(DATA_FOLDER, exist_ok=True)


# ============================================================
# FUNCIONES
# ============================================================

def load_afk():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_afk(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def format_duration(seconds: int) -> str:
    seconds = int(seconds)

    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []

    if days:
        parts.append(f"{days} día{'s' if days != 1 else ''}")

    if hours:
        parts.append(f"{hours} hora{'s' if hours != 1 else ''}")

    if minutes:
        parts.append(f"{minutes} minuto{'s' if minutes != 1 else ''}")

    if seconds and not parts:
        parts.append(f"{seconds} segundo{'s' if seconds != 1 else ''}")

    if not parts:
        return "menos de un segundo"

    return ", ".join(parts)


# ============================================================
# COG AFK
# ============================================================

class AFK(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.afk_users = load_afk()

    # ========================================================
    # /afk
    # ========================================================

    @app_commands.command(
        name="afk",
        description="Ponete en AFK."
    )
    @app_commands.describe(
        razon="Razón por la que estás AFK."
    )
    async def afk(
        self,
        interaction: discord.Interaction,
        razon: str = "Sin razón"
    ):

        user_id = str(interaction.user.id)

        # Si ya estaba AFK
        if user_id in self.afk_users:
            return await interaction.response.send_message(
                "❌ Ya estás en modo AFK.",
                ephemeral=True
            )

        now = datetime.now(timezone.utc)

        self.afk_users[user_id] = {
            "reason": razon,
            "timestamp": now.timestamp()
        }

        save_afk(self.afk_users)

        embed = discord.Embed(
            title="💤 Modo AFK",
            description=(
                f"{interaction.user.mention} ahora está **AFK**.\n\n"
                f"**Razón:** {razon}\n"
                f"**Desde:** <t:{int(now.timestamp())}:R>"
            ),
            color=discord.Color.from_rgb(128, 0, 255)
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ========================================================
    # MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # Ignorar bots
        if message.author.bot:
            return

        user_id = str(message.author.id)

        # ====================================================
        # QUITAR AFK AL VOLVER
        # ====================================================

        if user_id in self.afk_users:

            data = self.afk_users[user_id]

            start_time = data.get("timestamp")

            if start_time:
                elapsed = int(
                    datetime.now(timezone.utc).timestamp()
                    - start_time
                )
            else:
                elapsed = 0

            del self.afk_users[user_id]

            save_afk(self.afk_users)

            embed = discord.Embed(
                title="👋 Bienvenido de vuelta",
                description=(
                    f"{message.author.mention}, "
                    f"ya no estás AFK.\n\n"
                    f"Estuviste AFK durante **"
                    f"{format_duration(elapsed)}**."
                ),
                color=discord.Color.green()
            )

            await message.channel.send(
                embed=embed,
                delete_after=8
            )

        # ====================================================
        # AVISAR SI MENCIONAN A ALGUIEN AFK
        # ====================================================

        for member in message.mentions:

            if member.bot:
                continue

            target_id = str(member.id)

            if target_id not in self.afk_users:
                continue

            data = self.afk_users[target_id]

            reason = data.get(
                "reason",
                "Sin razón"
            )

            timestamp = data.get(
                "timestamp",
                datetime.now(timezone.utc).timestamp()
            )

            elapsed = int(
                datetime.now(timezone.utc).timestamp()
                - timestamp
            )

            embed = discord.Embed(
                title="💤 Usuario AFK",
                description=(
                    f"{member.mention} está **AFK**.\n\n"
                    f"**Razón:** {reason}\n"
                    f"**Hace:** {format_duration(elapsed)}\n"
                    f"**Desde:** <t:{int(timestamp)}:R>"
                ),
                color=discord.Color.from_rgb(128, 0, 255)
            )

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

            await message.channel.send(
                embed=embed,
                delete_after=10
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(AFK(bot))