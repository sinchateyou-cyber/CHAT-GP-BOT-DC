import discord
from discord import app_commands
from discord.ext import commands
class InvitesLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(
        name="invites-leaderboard",
        description="Muestra el ranking de invitaciones."
    )
    async def invites_leaderboard(
        self,
        interaction: discord.Interaction
    ):
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
        if not guild_data:
            await interaction.response.send_message(
                "❌ Todavía no hay invitaciones registradas.",
                ephemeral=True
            )
            return
        ranking = sorted(
            guild_data.items(),
            key=lambda x: x[1],
            reverse=True
        )
        descripcion = ""
        for posicion, (user_id, cantidad) in enumerate(
            ranking[:10],
            start=1
        ):
            usuario = interaction.guild.get_member(
                user_id
            )
            nombre = (
                usuario.mention
                if usuario
                else f"<@{user_id}>"
            )
            if posicion == 1:
                emoji = "🥇"
            elif posicion == 2:
                emoji = "🥈"
            elif posicion == 3:
                emoji = "🥉"
            else:
                emoji = f"`#{posicion}`"
            descripcion += (
                f"{emoji} {nombre} — "
                f"**{cantidad}** invitación(es)\n"
            )
        embed = discord.Embed(
            title="🏆 Ranking de Invitaciones",
            description=descripcion,
            color=discord.Color.gold()
        )
        await interaction.response.send_message(
            embed=embed
        )
async def setup(bot):
    await bot.add_cog(InvitesLeaderboard(bot))