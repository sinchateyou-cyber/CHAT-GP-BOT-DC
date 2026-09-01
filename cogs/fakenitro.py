import random
import string

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# GENERAR CÓDIGO FICTICIO
# ============================================================

def generar_codigo():

    caracteres = string.ascii_uppercase + string.digits

    partes = []

    for _ in range(3):

        parte = "".join(
            random.choice(caracteres)
            for _ in range(6)
        )

        partes.append(parte)

    return "DEMO-" + "-".join(partes)


# ============================================================
# VIEW
# ============================================================

class FakeNitroView(discord.ui.View):

    def __init__(self, codigo):

        super().__init__(
            timeout=120
        )

        self.codigo = codigo

    @discord.ui.button(
        label="🎁 Abrir regalo",
        style=discord.ButtonStyle.primary
    )
    async def abrir(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🎁 Regalo abierto",
            description=(
                "💜 **Discord Nitro — SIMULACIÓN**\n\n"
                "Este regalo es una demostración "
                "y no entrega Nitro real.\n\n"
                f"🎟️ **Código ficticio:**\n"
                f"```{self.codigo}```\n\n"
                "⚠️ **DEMO — CÓDIGO NO VÁLIDO**"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text="Fake Nitro • Simulación"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )


# ============================================================
# COG
# ============================================================

class FakeNitro(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "🎁 FakeNitro iniciado."
        )

    # ========================================================
    # /fakenitro
    # ========================================================

    @app_commands.command(
        name="fakenitro",
        description="Crea un regalo Nitro ficticio para una broma."
    )
    @app_commands.describe(
        usuario="Persona a la que querés regalar el Nitro ficticio."
    )
    async def fakenitro(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        codigo = generar_codigo()

        embed = discord.Embed(
            title="🎁 Discord Nitro",
            description=(
                f"💜 **{interaction.user.mention}** "
                f"te envió un regalo a {usuario.mention}.\n\n"
                "✨ **Nitro Gift — SIMULACIÓN**\n\n"
                "🎟️ Código ficticio:\n"
                f"```{codigo}```\n\n"
                "⚠️ **DEMO — NO ES UN CÓDIGO REAL**"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_thumbnail(
            url=(
                "https://cdn.discordapp.com/"
                "embed/avatars/0.png"
            )
        )

        embed.set_footer(
            text="Fake Nitro • Simulación"
        )

        view = FakeNitroView(
            codigo
        )

        await interaction.response.send_message(
            embed=embed,
            view=view
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        FakeNitro(bot)
    )
