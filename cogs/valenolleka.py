import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# BOTÓN
# ============================================================

class ValenollekaButton(discord.ui.Button):

    def __init__(
        self,
        texto_boton: str,
        url: str
    ):

        super().__init__(
            label=texto_boton[:80],
            style=discord.ButtonStyle.link,
            url=url
        )


# ============================================================
# VIEW
# ============================================================

class ValenollekaView(discord.ui.View):

    def __init__(
        self,
        texto_boton: str,
        url: str
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            ValenollekaButton(
                texto_boton,
                url
            )
        )


# ============================================================
# COG
# ============================================================

class Valenolleka(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ========================================================
    # /valenolleka
    # ========================================================

    @app_commands.command(
        name="valenolleka",
        description="Crea un mensaje con un botón que lleva a una página."
    )
    @app_commands.describe(
        titulo="Título que aparecerá arriba.",
        texto="Texto del mensaje.",
        boton="Texto que tendrá el botón.",
        url="Página a la que llevará el botón."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def valenolleka(
        self,
        interaction: discord.Interaction,
        titulo: str,
        texto: str,
        boton: str,
        url: str
    ):

        # ----------------------------------------------------
        # PERMISOS
        # ----------------------------------------------------

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Necesitás permisos de administrador.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # VALIDAR URL
        # ----------------------------------------------------

        url = url.strip()

        if not (
            url.startswith("https://")
            or url.startswith("http://")
        ):

            return await interaction.response.send_message(
                "❌ La URL tiene que empezar con `https://` o `http://`.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title=titulo[:256],
            description=texto,
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text=interaction.guild.name
        )

        # ----------------------------------------------------
        # VIEW
        # ----------------------------------------------------

        view = ValenollekaView(
            boton,
            url
        )

        # ----------------------------------------------------
        # ENVIAR
        # ----------------------------------------------------

        await interaction.channel.send(
            embed=embed,
            view=view
        )

        await interaction.response.send_message(
            "✅ Mensaje creado correctamente.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Valenolleka(bot)
    )
