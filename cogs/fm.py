import os
import urllib.parse
import aiohttp
import discord
from discord.ext import commands

class FM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Diccionario para almacenar tokens de Spotify
        # NOTA: En producción se recomienda guardar esto en una base de datos (SQLite, PostgreSQL, etc.)
        self.user_tokens = {}

    @commands.group(name="fm", invoke_without_command=True)
    async def fm(self, ctx):
        """Muestra la canción que el usuario está escuchando actualmente en Spotify."""
        token = self.user_tokens.get(ctx.author.id)
        if not token:
            return await ctx.send("❌ No has vinculado tu cuenta. Usa `s!fm login` primero.")

        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers) as resp:
                if resp.status == 204 or resp.status != 200:
                    return await ctx.send("🔇 No estás escuchando nada en Spotify en este momento.")
                
                data = await resp.json()
                if not data.get("is_playing"):
                    return await ctx.send("🔇 La reproducción está pausada.")

                track = data["item"]
                track_name = track["name"]
                artists = ", ".join([a["name"] for a in track["artists"]])
                album_name = track["album"]["name"]
                album_art = track["album"]["images"][0]["url"] if track["album"]["images"] else None
                track_url = track["external_urls"]["spotify"]

                embed = discord.Embed(
                    title=track_name,
                    url=track_url,
                    description=f"de **{artists}**\nÁlbum: *{album_name}*",
                    color=discord.Color.from_rgb(29, 185, 84)
                )
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                if album_art:
                    embed.set_thumbnail(url=album_art)
                embed.set_footer(text="Spotify", icon_url="https://i.imgur.com/7Fl4UOf.png")

                await ctx.send(embed=embed)

    @fm.command(name="login")
    async def login(self, ctx):
        """Genera el enlace para autorizar la cuenta de Spotify."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

        if not client_id or not redirect_uri:
            return await ctx.send("❌ La configuración de Spotify no está completa en el servidor.")

        scopes = "user-read-currently-playing user-read-recently-played"
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scopes
        }
        auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

        embed = discord.Embed(
            title="🔗 Vincula tu Spotify",
            description=f"Haz clic en el siguiente enlace para iniciar sesión:\n[Autorizar Spotify]({auth_url})",
            color=discord.Color.from_rgb(29, 185, 84)
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FM(bot))
