import discord
from discord.ext import commands
from discord import app_commands


class Say(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="say",
        description="Envía un anuncio personalizado."
    )
    @app_commands.describe(
        titulo="Título del anuncio",
        mensaje="Mensaje del anuncio",
        imagen="Imagen opcional"
    )
    async def say(
        self,
        interaction: discord.Interaction,
        titulo: str,
        mensaje: str,
        imagen: discord.Attachment = None
    ):

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ No tenés permisos.",
                ephemeral=True
            )
            return


        embed = discord.Embed(
            title=f"⬛💜 {titulo}",
            description=mensaje,
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )


        if imagen:

            if imagen.content_type.startswith("image"):
                embed.set_image(
                    url=imagen.url
                )


        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar.url
        )


        embed.set_footer(
            text=f"💜 {interaction.guild.name}"
        )


        await interaction.response.send_message(
            "✅ Anuncio enviado.",
            ephemeral=True
        )


        await interaction.channel.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Say(bot)
    )