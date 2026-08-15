import discord
from discord.ext import commands
from discord import app_commands

import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)

COIN = "💵"

MIN_BET = 10
MAX_BET = 1_000_000_000


# ============================================================
# COG APUESTAS
# ============================================================

class Apuestas(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "[APUESTAS] Cog cargado correctamente."
        )

    # ========================================================
    # OBTENER ECONOMÍA
    # ========================================================

    def get_economia(self):

        economia = self.bot.get_cog(
            "Economia"
        )

        return economia

    # ========================================================
    # OBTENER USUARIO
    # ========================================================

    def get_user_data(
        self,
        user_id
    ):

        economia = self.get_economia()

        if economia is None:

            return None, None

        data = economia.get_user(
            user_id
        )

        return economia, data

    # ========================================================
    # FORMATEAR DINERO
    # ========================================================

    def money(
        self,
        economia,
        amount
    ):

        return economia.format_money(
            amount
        )

    # ========================================================
    # VALIDAR APUESTA
    # ========================================================

    async def validate_bet(
        self,
        ctx,
        cantidad
    ):

        economia, data = self.get_user_data(
            ctx.author.id
        )

        if economia is None:

            await ctx.send(
                "❌ El sistema de economía no está cargado."
            )

            return None, None

        if cantidad < MIN_BET:

            await ctx.send(
                f"❌ La apuesta mínima es "
                f"{COIN} **${self.money(economia, MIN_BET)}**."
            )

            return None, None

        if cantidad > MAX_BET:

            await ctx.send(
                f"❌ La apuesta máxima es "
                f"{COIN} **${self.money(economia, MAX_BET)}**."
            )

            return None, None

        if data["money"] < cantidad:

            await ctx.send(
                "❌ **No tenés suficiente dinero.**\n\n"
                f"💰 Saldo: {COIN} "
                f"**${self.money(economia, data['money'])}**\n"
                f"🎲 Apuesta: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            return None, None

        return economia, data

    # ========================================================
    # APOSTAR
    # ========================================================

    @commands.hybrid_command(
        name="apostar",
        description="Hacé una apuesta 50/50."
    )
    @app_commands.describe(
        cantidad="Cantidad de dinero que querés apostar."
    )
    async def apostar(
        self,
        ctx,
        cantidad: app_commands.Range[
            int,
            MIN_BET,
            MAX_BET
        ]
    ):

        economia, data = await self.validate_bet(
            ctx,
            cantidad
        )

        if economia is None:
            return

        resultado = random.choice(
            [
                "ganar",
                "perder"
            ]
        )

        # ----------------------------------------------------
        # GANAR
        # ----------------------------------------------------

        if resultado == "ganar":

            data["money"] += cantidad
            data["wins"] = data.get(
                "wins",
                0
            ) + 1

            mensaje = (
                f"🎉 **GANASTE**\n\n"
                f"Ganancia: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            color = discord.Color.green()

        # ----------------------------------------------------
        # PERDER
        # ----------------------------------------------------

        else:

            data["money"] -= cantidad
            data["losses"] = data.get(
                "losses",
                0
            ) + 1

            mensaje = (
                f"💀 **PERDISTE**\n\n"
                f"Pérdida: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            color = discord.Color.red()

        economia.save_data()

        embed = discord.Embed(
            title="🎲・APUESTA",
            description=mensaje,
            color=color
        )

        embed.add_field(
            name="💰 Saldo actual",
            value=(
                f"{COIN} "
                f"**${self.money(economia, data['money'])}**"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Apuesta de {ctx.author.display_name}"
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # RULETA
    # ========================================================

    @commands.hybrid_command(
        name="ruleta",
        description="Apostá al rojo o negro en la ruleta."
    )
    @app_commands.describe(
        cantidad="Cantidad que querés apostar.",
        color="Elegí rojo o negro."
    )
    @app_commands.choices(
        color=[
            app_commands.Choice(
                name="🔴 Rojo",
                value="rojo"
            ),
            app_commands.Choice(
                name="⚫ Negro",
                value="negro"
            )
        ]
    )
    async def ruleta(
        self,
        ctx,
        cantidad: app_commands.Range[
            int,
            MIN_BET,
            MAX_BET
        ],
        color: str
    ):

        color = color.lower()

        if color not in (
            "rojo",
            "negro"
        ):

            await ctx.send(
                "❌ Elegí **rojo** o **negro**."
            )

            return

        economia, data = await self.validate_bet(
            ctx,
            cantidad
        )

        if economia is None:
            return

        # ----------------------------------------------------
        # RULETA
        # ----------------------------------------------------

        numero = random.randint(
            0,
            36
        )

        if numero == 0:

            resultado_color = "verde"

        elif numero in {
            1, 3, 5, 7, 9,
            12, 14, 16, 18,
            19, 21, 23, 25,
            27, 30, 32, 34, 36
        }:

            resultado_color = "rojo"

        else:

            resultado_color = "negro"

        # ----------------------------------------------------
        # GANADOR
        # ----------------------------------------------------

        if resultado_color == color:

            # +cantidad = ganancia neta
            data["money"] += cantidad

            data["wins"] = data.get(
                "wins",
                0
            ) + 1

            mensaje = (
                f"🎉 **¡GANASTE LA RULETA!**\n\n"
                f"🎱 Número: **{numero}**\n"
                f"🎨 Color: **{resultado_color.upper()}**\n\n"
                f"Ganaste: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            embed_color = discord.Color.green()

        # ----------------------------------------------------
        # PERDEDOR
        # ----------------------------------------------------

        else:

            data["money"] -= cantidad

            data["losses"] = data.get(
                "losses",
                0
            ) + 1

            mensaje = (
                f"💀 **PERDISTE LA RULETA**\n\n"
                f"🎱 Número: **{numero}**\n"
                f"🎨 Color: **{resultado_color.upper()}**\n\n"
                f"Perdiste: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            embed_color = discord.Color.red()

        economia.save_data()

        embed = discord.Embed(
            title="🎰・RULETA",
            description=mensaje,
            color=embed_color
        )

        embed.add_field(
            name="💰 Saldo actual",
            value=(
                f"{COIN} "
                f"**${self.money(economia, data['money'])}**"
            ),
            inline=False
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # BLACKJACK
    # ========================================================

    @commands.hybrid_command(
        name="blackjack",
        description="Jugá blackjack contra el bot."
    )
    @app_commands.describe(
        cantidad="Cantidad que querés apostar."
    )
    async def blackjack(
        self,
        ctx,
        cantidad: app_commands.Range[
            int,
            MIN_BET,
            MAX_BET
        ]
    ):

        economia, data = await self.validate_bet(
            ctx,
            cantidad
        )

        if economia is None:
            return

        # ----------------------------------------------------
        # CARTAS
        # ----------------------------------------------------

        player = [
            random.randint(1, 11),
            random.randint(1, 11)
        ]

        dealer = [
            random.randint(1, 11),
            random.randint(1, 11)
        ]

        player_total = sum(
            player
        )

        dealer_total = sum(
            dealer
        )

        # ----------------------------------------------------
        # AJUSTE SIMPLE DE AS
        # ----------------------------------------------------

        if player_total > 21:

            player_total -= 10

        if dealer_total > 21:

            dealer_total -= 10

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        if player_total > 21:

            resultado = "perder"

        elif dealer_total > 21:

            resultado = "ganar"

        elif player_total > dealer_total:

            resultado = "ganar"

        elif player_total < dealer_total:

            resultado = "perder"

        else:

            resultado = "empate"

        # ----------------------------------------------------
        # GANAR
        # ----------------------------------------------------

        if resultado == "ganar":

            data["money"] += cantidad

            data["wins"] = data.get(
                "wins",
                0
            ) + 1

            mensaje = (
                "🎉 **¡GANASTE!**\n\n"
                f"👤 Tus cartas: **{player_total}**\n"
                f"🤖 Cartas del bot: **{dealer_total}**\n\n"
                f"Ganaste: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            embed_color = discord.Color.green()

        # ----------------------------------------------------
        # PERDER
        # ----------------------------------------------------

        elif resultado == "perder":

            data["money"] -= cantidad

            data["losses"] = data.get(
                "losses",
                0
            ) + 1

            mensaje = (
                "💀 **PERDISTE**\n\n"
                f"👤 Tus cartas: **{player_total}**\n"
                f"🤖 Cartas del bot: **{dealer_total}**\n\n"
                f"Perdiste: {COIN} "
                f"**${self.money(economia, cantidad)}**"
            )

            embed_color = discord.Color.red()

        # ----------------------------------------------------
        # EMPATE
        # ----------------------------------------------------

        else:

            mensaje = (
                "🤝 **EMPATE**\n\n"
                f"👤 Tus cartas: **{player_total}**\n"
                f"🤖 Cartas del bot: **{dealer_total}**\n\n"
                "No ganaste ni perdiste dinero."
            )

            embed_color = discord.Color.gold()

        economia.save_data()

        embed = discord.Embed(
            title="🃏・BLACKJACK",
            description=mensaje,
            color=embed_color
        )

        embed.add_field(
            name="💰 Saldo actual",
            value=(
                f"{COIN} "
                f"**${self.money(economia, data['money'])}**"
            ),
            inline=False
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # ESTADÍSTICAS DE APUESTAS
    # ========================================================

    @commands.hybrid_command(
        name="statsapuestas",
        description="Muestra tus estadísticas de apuestas."
    )
    async def statsapuestas(
        self,
        ctx
    ):

        economia, data = self.get_user_data(
            ctx.author.id
        )

        if economia is None:

            await ctx.send(
                "❌ El sistema de economía no está cargado."
            )

            return

        wins = data.get(
            "wins",
            0
        )

        losses = data.get(
            "losses",
            0
        )

        total_games = (
            wins
            + losses
        )

        if total_games > 0:

            winrate = (
                wins
                / total_games
            ) * 100

        else:

            winrate = 0

        embed = discord.Embed(
            title="📊・ESTADÍSTICAS DE APUESTAS",
            description=(
                f"👤 **{ctx.author.display_name}**\n\n"
                f"🎉 Victorias: **{wins}**\n"
                f"💀 Derrotas: **{losses}**\n"
                f"🎮 Partidas: **{total_games}**\n"
                f"📈 Winrate: **{winrate:.1f}%**"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=ctx.author.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Apuestas(bot)
    )

    print(
        "[APUESTAS] Sistema de apuestas activado."
    )