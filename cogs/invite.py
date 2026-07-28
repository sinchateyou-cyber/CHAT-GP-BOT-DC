import discord
from discord import app_commands
from discord.ext import commands
class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # INVITE
    # =========================
    @app_commands.command(
        name="invite",
        description="Genera un enlace para invitar el bot a otro servidor."
    )
    async def invite(
        self,
        interaction: discord.Interaction
    ):
        # Generar enlace de invitación
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(
                administrator=True
            )
        )
        # Crear Embed
        embed = discord.Embed(
            title="🤖 ¡Invitá mi bot!",
            description=(
                f"[Hacé clic acá para invitarme "
                f"a tu servidor]({invite_url})"
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )
        embed.set_footer(
            text="¡Gracias por invitarme!"
        )
        # Enviar mensaje
        await interaction.response.send_message(
            embed=embed
        )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Invite(bot)
    )