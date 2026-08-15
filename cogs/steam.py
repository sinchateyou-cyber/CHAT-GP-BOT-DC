# cogs/steam.py

import os
import re
import aiohttp
import discord

from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

STEAM_API_KEY = os.getenv("STEAM_API_KEY")

STEAM_API = "https://api.steampowered.com"

REQUEST_TIMEOUT = 10


# ============================================================
# COG
# ============================================================

class Steam(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print("[STEAM] Cog cargado.")

        if STEAM_API_KEY:
            print("[STEAM] Steam API Key encontrada.")
        else:
            print("[STEAM] ⚠️ Falta STEAM_API_KEY.")


    # ========================================================
    # REQUEST
    # ========================================================

    async def api_request(
        self,
        endpoint,
        params
    ):

        url = f"{STEAM_API}{endpoint}"

        timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT
        )

        try:

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    url,
                    params=params
                ) as response:

                    if response.status != 200:
                        return None

                    return await response.json()

        except Exception as error:

            print(
                f"[STEAM] Error API: {error}"
            )

            return None


    # ========================================================
    # RESOLVER STEAM ID
    # ========================================================

    async def resolve_steam_id(
        self,
        entrada
    ):

        entrada = entrada.strip()

        # ----------------------------------------------------
        # STEAMID64
        # ----------------------------------------------------

        if entrada.isdigit():

            if len(entrada) >= 15:
                return entrada

        # ----------------------------------------------------
        # LIMPIAR URL
        # ----------------------------------------------------

        entrada = entrada.rstrip("/")


        # ====================================================
        # URL /profiles/STEAMID64
        # ====================================================

        profile_match = re.search(
            r"steamcommunity\.com/profiles/(\d+)",
            entrada,
            re.IGNORECASE
        )

        if profile_match:

            return profile_match.group(1)


        # ====================================================
        # URL /id/vanity
        # ====================================================

        vanity_match = re.search(
            r"steamcommunity\.com/id/([^/?]+)",
            entrada,
            re.IGNORECASE
        )

        if vanity_match:

            vanity = vanity_match.group(1)

        else:

            # Si escribió solamente el nombre
            vanity = entrada


        # ====================================================
        # RESOLVER VANITY
        # ====================================================

        data = await self.api_request(
            "/ISteamUser/ResolveVanityURL/v1/",
            {
                "key": STEAM_API_KEY,
                "vanityurl": vanity
            }
        )

        if not data:
            return None

        response = data.get(
            "response",
            {}
        )

        if response.get("success") != 1:
            return None

        return response.get(
            "steamid"
        )


    # ========================================================
    # OBTENER PERFIL
    # ========================================================

    async def get_profile(
        self,
        steam_id
    ):

        data = await self.api_request(
            "/ISteamUser/GetPlayerSummaries/v2/",
            {
                "key": STEAM_API_KEY,
                "steamids": steam_id
            }
        )

        if not data:
            return None

        players = (
            data
            .get("response", {})
            .get("players", [])
        )

        if not players:
            return None

        return players[0]


    # ========================================================
    # JUEGOS
    # ========================================================

    async def get_games(
        self,
        steam_id
    ):

        data = await self.api_request(
            "/IPlayerService/GetOwnedGames/v1/",
            {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "include_appinfo": 1,
                "include_played_free_games": 1
            }
        )

        if not data:
            return []

        return (
            data
            .get("response", {})
            .get("games", [])
        )


    # ========================================================
    # LOGROS
    # ========================================================

    async def get_achievements(
        self,
        steam_id,
        appid
    ):

        data = await self.api_request(
            "/ISteamUserStats/GetPlayerAchievements/v1/",
            {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "appid": appid
            }
        )

        if not data:
            return None

        return data.get(
            "playerstats"
        )


    # ========================================================
    # ESTADO
    # ========================================================

    def get_status(
        self,
        profile
    ):

        state = profile.get(
            "personastate",
            0
        )

        states = {
            0: "⚫ Offline",
            1: "🟢 Online",
            2: "🔴 Ocupado",
            3: "🌙 Ausente",
            4: "🟠 Durmiendo",
            5: "🟠 Buscando intercambio",
            6: "🟠 Buscando jugar"
        }

        return states.get(
            state,
            "⚫ Offline"
        )


    # ========================================================
    # HORAS
    # ========================================================

    def format_hours(
        self,
        minutes
    ):

        hours = minutes / 60

        if hours >= 1000:
            return f"{hours:,.0f} h"

        if hours >= 100:
            return f"{hours:,.1f} h"

        return f"{hours:.1f} h"


    # ========================================================
    # FECHA
    # ========================================================

    def format_created(
        self,
        timestamp
    ):

        if not timestamp:
            return "Oculta"

        try:

            from datetime import datetime

            date = datetime.fromtimestamp(
                timestamp
            )

            return date.strftime(
                "%d/%m/%Y"
            )

        except Exception:

            return "Desconocida"


    # ========================================================
    # EMBED
    # ========================================================

    async def create_profile_embed(
        self,
        steam_id
    ):

        profile = await self.get_profile(
            steam_id
        )

        if not profile:
            return None

        games = await self.get_games(
            steam_id
        )

        # ----------------------------------------------------
        # DATOS
        # ----------------------------------------------------

        name = profile.get(
            "personaname",
            "Usuario desconocido"
        )

        avatar = profile.get(
            "avatarfull"
        )

        profile_url = profile.get(
            "profileurl",
            f"https://steamcommunity.com/profiles/{steam_id}"
        )

        status = self.get_status(
            profile
        )

        created = self.format_created(
            profile.get(
                "timecreated"
            )
        )

        game_count = len(
            games
        )

        total_minutes = sum(
            game.get(
                "playtime_forever",
                0
            )
            for game in games
        )

        total_hours = self.format_hours(
            total_minutes
        )

        # ----------------------------------------------------
        # JUEGO ACTUAL
        # ----------------------------------------------------

        current_game = profile.get(
            "gameextrainfo"
        )

        if current_game:

            playing = (
                f"🎮 **Jugando ahora:** "
                f"{current_game}"
            )

        else:

            playing = (
                "🎮 **Jugando ahora:** "
                "Ninguno"
            )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(

            title=f"🎮 Steam · {name}",

            description=(
                f"{status}\n\n"
                f"{playing}"
            ),

            color=discord.Color.from_rgb(
                102,
                192,
                244
            ),

            url=profile_url
        )

        if avatar:
            embed.set_thumbnail(
                url=avatar
            )

        embed.add_field(
            name="🆔 SteamID64",
            value=f"`{steam_id}`",
            inline=False
        )

        embed.add_field(
            name="🎮 Juegos",
            value=f"**{game_count}**",
            inline=True
        )

        embed.add_field(
            name="⏱️ Horas jugadas",
            value=f"**{total_hours}**",
            inline=True
        )

        embed.add_field(
            name="📅 Cuenta creada",
            value=f"**{created}**",
            inline=True
        )

        # ----------------------------------------------------
        # TOP 5 JUEGOS
        # ----------------------------------------------------

        if games:

            top_games = sorted(
                games,
                key=lambda game: game.get(
                    "playtime_forever",
                    0
                ),
                reverse=True
            )[:5]

            lines = []

            for index, game in enumerate(
                top_games,
                start=1
            ):

                game_name = game.get(
                    "name",
                    "Juego desconocido"
                )

                minutes = game.get(
                    "playtime_forever",
                    0
                )

                hours = self.format_hours(
                    minutes
                )

                lines.append(
                    f"`{index}.` **{game_name}** — `{hours}`"
                )

            embed.add_field(
                name="🏆 Juegos más jugados",
                value="\n".join(lines),
                inline=False
            )

        else:

            embed.add_field(
                name="🏆 Juegos",
                value=(
                    "No se pudieron obtener "
                    "los juegos de esta cuenta.\n"
                    "Probablemente la biblioteca "
                    "sea privada."
                ),
                inline=False
            )

        embed.set_footer(
            text="Steam Statistics"
        )

        return embed


    # ========================================================
    # COMANDO HÍBRIDO
    #
    # /steam
    # s!steam
    # ========================================================

    @commands.hybrid_command(
        name="steam",
        description="Muestra las estadísticas de una cuenta de Steam."
    )
    @app_commands.describe(
        usuario=(
            "SteamID64, URL del perfil "
            "o nombre personalizado de Steam."
        )
    )
    async def steam(
        self,
        ctx: commands.Context,
        usuario: str
    ):

        # ----------------------------------------------------
        # API KEY
        # ----------------------------------------------------

        if not STEAM_API_KEY:

            await ctx.send(
                "❌ El bot no tiene configurada "
                "la **Steam API Key**.\n\n"
                "Agregá `STEAM_API_KEY` en las "
                "variables de entorno de Render."
            )

            return

        # ----------------------------------------------------
        # BUSCANDO
        # ----------------------------------------------------

        try:

            await ctx.defer()

        except Exception:

            pass

        # ----------------------------------------------------
        # RESOLVER ID
        # ----------------------------------------------------

        steam_id = await self.resolve_steam_id(
            usuario
        )

        if not steam_id:

            await ctx.send(
                "❌ No pude encontrar esa cuenta de Steam.\n\n"
                "Podés usar:\n"
                "• SteamID64\n"
                "• URL del perfil\n"
                "• URL personalizada de Steam\n"
                "• Nombre personalizado"
            )

            return

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = await self.create_profile_embed(
            steam_id
        )

        if not embed:

            await ctx.send(
                "❌ No pude obtener las estadísticas "
                "de esa cuenta de Steam.\n\n"
                "Puede que el perfil no exista, "
                "sea privado o que Steam no permita "
                "consultar sus datos."
            )

            return

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Steam(bot)
    )

    print(
        "[STEAM] Extension cargada correctamente."
    )