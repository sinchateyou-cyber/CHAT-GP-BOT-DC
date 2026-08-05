import discord
from discord.ext import commands
from discord import app_commands


class Say(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="say",
        description="Envía un mensaje personalizado con embed."
    )
    @app_commands.describe(
        titulo="Título del embed",
        mensaje="Mensaje que enviará el bot",
        imagen="URL de imagen grande",
        thumbnail="URL de imagen pequeña",
        color="Color hexadecimal (ej: #8000ff)"
    )
    async def say(
        self,
        interaction: discord.Interaction,
        titulo: str,
        mensaje: str,
        imagen: str = None,
        thumbnail: str = None,
        color: str = "#8000ff"
    ):

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ No tenés permisos.",
                ephemeral=True
            )
            return


        try:
            color_embed = int(
                color.replace("#", ""),
                16
            )
        except:
            color_embed = 0x8000FF


        embed = discord.Embed(
            title=f"⬛💜 {titulo}",
            description=mensaje,
            color=color_embed
        )


        if imagen:
            embed.set_image(
                url=imagen
            )


        if thumbnail:
            embed.set_thumbnail(
                url=thumbnail
            )


        embed.set_author(
            name=interaction.user.name,
            icon_url=interaction.user.display_avatar.url
        )


        embed.set_footer(
            text=f"💜 {interaction.guild.name}"
        )


        await interaction.response.send_message(
            "✅ Mensaje enviado.",
            ephemeral=True
        )


        await interaction.channel.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                everyone=True,
                users=True,
                roles=True
            )
        )


async def setup(bot):
    await bot.add_cog(
        Say(bot)
    )