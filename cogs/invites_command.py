import discord
from discord import app_commands
from discord.ext import commands
class InvitesCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(
        name="invites",
        description="Muestra las invitaciones de un usuario."
    )
    @app_commands.describe(
        usuario="Usuario que quieres consultar."
    )
    async def invites(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member = None
    ):
        usuario = usuario or interaction.user
        tracker = self.bot.get_cog("InviteTracker")
        if tracker is None:
            await interaction.response.send_message(
                "❌ El sistema de invitaciones no está activo.",
                ephemeral=True
            )
            return
        guild_data = tracker.invite_counts.get(
            interaction.guild.id,
            {}
        )
        cantidad = guild_data.get(usuario.id, 0)
        embed = discord.Embed(
            title="📨 Invitaciones",
            description=(
                f"{usuario.mention} tiene "
                f"**{cantidad}** invitación(es)."
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )
        await interaction.response.send_message(
            embed=embed
        )
async def setup(bot):
    await bot.add_cog(InvitesCommand(bot))