import random
import discord
from discord.ext import commands
from discord import app_commands


GIFS = {
    "beso": [
        "https://tenor.com/bBjasgVPruB.gif",
        "https://tenor.com/bohKF.gif",
        "https://tenor.com/bKJY1.gif",
    ],

    "hug": [
        "https://tenor.com/bUwEv.gif",
        "https://tenor.com/dw0XbsEOm7J.gif",
    ],

    "mimos": [
        "https://tenor.com/bvRt9.gif",
    ],

    "punch": []
}


ACCIONES = {
    "beso": {
        "emoji": "💋",
        "texto": "le dio un beso a",
        "devuelto": "le devolvió el beso a",
    },
    "hug": {
        "emoji": "🤗",
        "texto": "abrazó a",
        "devuelto": "le devolvió el abrazo a",
    },
    "mimos": {
        "emoji": "🥰",
        "texto": "le hizo mimos a",
        "devuelto": "le devolvió los mimos a",
    },
    "punch": {
        "emoji": "👊",
        "texto": "le dio un golpe a",
        "devuelto": "le devolvió el golpe a",
    },
}


def elegir_gif(accion: str, anterior: str | None = None):

    gifs = GIFS.get(accion, [])

    if not gifs:
        return None

    disponibles = [
        gif for gif in gifs
        if gif != anterior
    ]

    if not disponibles:
        disponibles = gifs

    return random.choice(disponibles)


class InteraccionView(discord.ui.View):

    def __init__(
        self,
        autor: discord.Member,
        objetivo: discord.Member,
        accion: str,
        gif_actual: str | None
    ):
        super().__init__(timeout=60)

        self.autor = autor
        self.objetivo = objetivo
        self.accion = accion
        self.gif_actual = gif_actual

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:

        if interaction.user.id != self.objetivo.id:

            await interaction.response.send_message(
                "❌ Solo la persona mencionada puede responder.",
                ephemeral=True
            )

            return False

        return True

    @discord.ui.button(
        label="Devolver",
        emoji="↩️",
        style=discord.ButtonStyle.primary
    )
    async def devolver(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        datos = ACCIONES[self.accion]

        gif = elegir_gif(
            self.accion,
            self.gif_actual
        )

        embed = discord.Embed(
            description=(
                f"{datos['emoji']} "
                f"**{self.objetivo.display_name}** "
                f"{datos['devuelto']} "
                f"**{self.autor.display_name}**."
            ),
            color=discord.Color.from_rgb(
                128, 0, 255
            )
        )

        if gif:
            embed.set_image(url=gif)

        embed.set_footer(
            text="Interacciones"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Rechazar",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def rechazar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            description=(
                f"❌ **{self.objetivo.display_name}** "
                f"rechazó la interacción de "
                f"**{self.autor.display_name}**."
            ),
            color=discord.Color.red()
        )

        embed.set_footer(
            text="Interacciones"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )


class Interacciones(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def ejecutar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        accion: str
    ):

        if usuario.id == interaction.user.id:

            await interaction.response.send_message(
                "❌ No podés hacer esto con vos mismo.",
                ephemeral=True
            )

            return

        datos = ACCIONES[accion]

        gif = elegir_gif(accion)

        embed = discord.Embed(
            description=(
                f"{datos['emoji']} "
                f"**{interaction.user.display_name}** "
                f"{datos['texto']} "
                f"**{usuario.display_name}**."
            ),
            color=discord.Color.from_rgb(
                128, 0, 255
            )
        )

        if gif:
            embed.set_image(url=gif)

        embed.set_footer(
            text="La persona mencionada puede responder."
        )

        await interaction.response.send_message(
            embed=embed,
            view=InteraccionView(
                interaction.user,
                usuario,
                accion,
                gif
            )
        )

    # ========================================================
    # BESO
    # ========================================================

    @app_commands.command(
        name="beso",
        description="Dale un beso a alguien."
    )
    async def beso(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.ejecutar(
            interaction,
            usuario,
            "beso"
        )

    # ========================================================
    # HUG
    # ========================================================

    @app_commands.command(
        name="hug",
        description="Dale un abrazo a alguien."
    )
    async def hug(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.ejecutar(
            interaction,
            usuario,
            "hug"
        )

    # ========================================================
    # MIMOS
    # ========================================================

    @app_commands.command(
        name="mimos",
        description="Dale mimos a alguien."
    )
    async def mimos(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.ejecutar(
            interaction,
            usuario,
            "mimos"
        )

    # ========================================================
    # PUNCH
    # ========================================================

    @app_commands.command(
        name="punch",
        description="Dale un golpe a alguien."
    )
    async def punch(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.ejecutar(
            interaction,
            usuario,
            "punch"
        )


async def setup(bot):
    await bot.add_cog(Interacciones(bot))