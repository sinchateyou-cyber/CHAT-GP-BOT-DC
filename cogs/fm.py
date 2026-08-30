 import discord
from discord.ext import commands

class FM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fm")
    async def fm(self, ctx, member: discord.Member = None):
        """Muestra la canción de Spotify que el usuario está escuchando en su estado de Discord."""
        member = member or ctx.author

        # Busca la actividad de Spotify en el estado del usuario
        spotify_activity = None
        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                spotify_activity = activity
                break

        if not spotify_activity:
            return await ctx.send(f"132 {member.display_name} no está escuchando Spotify en Discord en este momento.")

        # Extrae la información de la presencia
        track_name = spotify_activity.title
        artists = ", ".join(spotify_activity.artists)
        album_name = spotify_activity.album
        album_art = spotify_activity.album_cover_url
        track_url = spotify_activity.track_url

        embed = discord.Embed(
            title=track_name,
            url=track_url,
            description=f"de **{artists}**\nÁlbum: *{album_name}*",
            color=discord.Color.from_rgb(29, 185, 84)
        )
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        if album_art:
            embed.set_thumbnail(url=album_art)
        embed.set_footer(text="Spotify via Discord Presences", icon_url="https://i.imgur.com/7Fl4UOf.png")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FM(bot))
