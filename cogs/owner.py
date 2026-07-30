
import json
import os

import discord
from discord import app_commands
from discord.ext import commands
MAIN_OWNER_ID = 1460867297500594266


OWNERS_FILE = "data/owners.json"


def ensure_data_folder():
    os.makedirs("data", exist_ok=True)


def load_owners():
    ensure_data_folder()

    if not os.path.exists(OWNERS_FILE):
        return []

    try:
        with open(OWNERS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (json.JSONDecodeError, OSError):
        return []


def save_owners(owners):
    ensure_data_folder()

    with open(OWNERS_FILE, "w", encoding="utf-8") as file:
        json.dump(owners, file, indent=4)


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        ensure_data_folder()

    # ========================================================
    # /setowner
    # ========================================================
    if interaction.user.id != MAIN_OWNER_ID:
    await interaction.response.send_message(
        "❌ Solo el owner principal del bot puede usar este comando.",
        ephemeral=True
    )
    return

        # Solo el owner principal de Discord puede usarlo
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Solo el owner principal del bot puede usar este comando.",
                ephemeral=True
            )
            return

        owners = load_owners()

        if usuario.id in owners:
            await interaction.response.send_message(
                f"⚠️ {usuario.mention} ya es owner del bot.",
                ephemeral=True
            )
            return

        owners.append(usuario.id)
        save_owners(owners)

        await interaction.response.send_message(
            f"✅ {usuario.mention} ahora es owner del bot.",
            ephemeral=True
        )

    # ========================================================
    # /removeowner
    # ========================================================
    if interaction.user.id != MAIN_OWNER_ID:
    await interaction.response.send_message(
        "❌ Solo el owner principal del bot puede usar este comando.",
        ephemeral=True
    )
    return

        # Solo el owner principal puede quitar owners
        if interaction.user.id != self.bot.owner_id:
            await interaction.response.send_message(
                "❌ Solo el owner principal del bot puede usar este comando.",
                ephemeral=True
            )
            return

        owners = load_owners()

        if usuario.id not in owners:
            await interaction.response.send_message(
                f"⚠️ {usuario.mention} no es owner del bot.",
                ephemeral=True
            )
            return

        owners.remove(usuario.id)
        save_owners(owners)

        await interaction.response.send_message(
            f"✅ {usuario.mention} ya no es owner del bot.",
            ephemeral=True
        )

    # ========================================================
    # /owners
    # ========================================================

    @app_commands.command(
        name="owners",
        description="Muestra la lista de owners del bot."
    )
    async def owners(
        self,
        interaction: discord.Interaction
    ):

        owners = load_owners()

        if not owners:
            await interaction.response.send_message(
                "📋 No hay owners adicionales configurados.",
                ephemeral=True
            )
            return

        lista = []

        for owner_id in owners:
            usuario = self.bot.get_user(owner_id)

            if usuario:
                lista.append(
                    f"• {usuario.mention} (`{owner_id}`)"
                )
            else:
                lista.append(
                    f"• <@{owner_id}> (`{owner_id}`)"
                )

        embed = discord.Embed(
            title="👑 Owners del bot",
            description="\n".join(lista),
            color=discord.Color.gold()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Owner(bot))