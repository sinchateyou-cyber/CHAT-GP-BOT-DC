import discord
from discord.ext import commands
from discord import app_commands

import os
import json
import random
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(
    DATA_FOLDER,
    "economia.json"
)

# Tiempo entre robos
ROBO_COOLDOWN = 1800  # 30 minutos

# Probabilidad de éxito
SUCCESS_CHANCE = 0.55  # 55%

# Porcentaje máximo que podés robar
MIN_PERCENT = 0.10
MAX_PERCENT = 0.35

# Cantidad mínima que debe tener la víctima
MIN_VICTIM_MONEY = 100

# Límite máximo que se puede robar
MAX_STEAL = 10000

# Multa máxima al fallar
MAX_FINE = 1500

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)

DARK_PURPLE = discord.Color.from_rgb(
    75,
    30,
    150
)

COIN = "💵"


# ============================================================
# CARGAR ECONOMÍA
# ============================================================

def cargar_economia():

    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {},
                f,
                indent=4,
                ensure_ascii=False
            )

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if isinstance(
                data,
                dict
            ):

                return data

    except Exception as error:

        print(
            f"[ROBO] Error cargando economía: {error}"
        )

    return {}


# ============================================================
# GUARDAR ECONOMÍA
# ============================================================

def guardar_economia(data):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as error:

        print(
            f"[ROBO] Error guardando economía: {error}"
        )

        return False


# ============================================================
# FORMATO DINERO
# ============================================================

def format_money(amount):

    return f"{int(amount):,}".replace(
        ",",
        "."
    )


# ============================================================
# FORMATO TIEMPO
# ============================================================

def format_time(seconds):

    seconds = max(
        0,
        int(seconds)
    )

    minutes = seconds // 60
    seconds %= 60

    hours = minutes // 60
    minutes %= 60

    if hours > 0:

        return (
            f"{hours}h "
            f"{minutes}m "
            f"{seconds}s"
        )

    if minutes > 0:

        return (
            f"{minutes}m "
            f"{seconds}s"
        )

    return f"{seconds}s"


# ============================================================
# COG ROBO
# ============================================================

class Robo(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        # Cooldowns independientes por usuario
        self.cooldowns = {}

        print(
            "[ROBO] Sistema de robos cargado correctamente."
        )

    # ========================================================
    # OBTENER USUARIO
    # ========================================================

    def get_user(
        self,
        data,
        user_id
    ):

        user_id = str(
            user_id
        )

        if user_id not in data:

            data[user_id] = {
                "money": 1000,
                "bank": 0,
                "daily": 0,
                "work": 0,
                "wins": 0,
                "losses": 0,
                "inventory": []
            }

        # Compatibilidad con cuentas antiguas
        data[user_id].setdefault(
            "money",
            1000
        )

        data[user_id].setdefault(
            "bank",
            0
        )

        data[user_id].setdefault(
            "daily",
            0
        )

        data[user_id].setdefault(
            "work",
            0
        )

        data[user_id].setdefault(
            "wins",
            0
        )

        data[user_id].setdefault(
            "losses",
            0
        )

        data[user_id].setdefault(
            "inventory",
            []
        )

        return data[user_id]

    # ========================================================
    # ROBO
    # ========================================================

    @commands.hybrid_command(
        name="robar",
        description="Intentá robarle dinero a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés intentar robar."
    )
    async def robar(
        self,
        ctx,
        usuario: discord.Member
    ):

        # ----------------------------------------------------
        # VALIDACIONES
        # ----------------------------------------------------

        if usuario.bot:

            await ctx.send(
                "🤖 **No podés robarle a un bot.**"
            )

            return

        if usuario.id == ctx.author.id:

            await ctx.send(
                "💀 **No podés robarte a vos mismo.**"
            )

            return

        if usuario.guild.id != ctx.guild.id:

            await ctx.send(
                "❌ Ese usuario no pertenece a este servidor."
            )

            return

        # ----------------------------------------------------
        # COOLDOWN
        # ----------------------------------------------------

        now = time.time()

        last_robo = self.cooldowns.get(
            ctx.author.id,
            0
        )

        remaining = (
            last_robo
            + ROBO_COOLDOWN
            - now
        )

        if remaining > 0:

            embed = discord.Embed(
                title="⏳・ROBO EN COOLDOWN",
                description=(
                    f"Ya intentaste robar recientemente.\n\n"
                    f"🕐 Podés volver a intentarlo en "
                    f"**{format_time(remaining)}**."
                ),
                color=PURPLE
            )

            await ctx.send(
                embed=embed
            )

            return

        # ----------------------------------------------------
        # CARGAR ECONOMÍA
        # ----------------------------------------------------

        data = cargar_economia()

        robber = self.get_user(
            data,
            ctx.author.id
        )

        victim = self.get_user(
            data,
            usuario.id
        )

        victim_money = int(
            victim.get(
                "money",
                0
            )
        )

        robber_money = int(
            robber.get(
                "money",
                0
            )
        )

        # ----------------------------------------------------
        # VÍCTIMA SIN DINERO
        # ----------------------------------------------------

        if victim_money < MIN_VICTIM_MONEY:

            embed = discord.Embed(
                title="💸・ROBO IMPOSIBLE",
                description=(
                    f"Intentaste robarle a "
                    f"**{usuario.display_name}**.\n\n"
                    "Pero no tiene suficiente dinero "
                    "para que valga la pena."
                ),
                color=PURPLE
            )

            await ctx.send(
                embed=embed
            )

            return

        # ----------------------------------------------------
        # ACTIVAR COOLDOWN
        # ----------------------------------------------------

        self.cooldowns[
            ctx.author.id
        ] = now

        # ----------------------------------------------------
        # PROBABILIDAD
        # ----------------------------------------------------

        success = random.random() < SUCCESS_CHANCE

        # ====================================================
        # ÉXITO
        # ====================================================

        if success:

            percentage = random.uniform(
                MIN_PERCENT,
                MAX_PERCENT
            )

            stolen = int(
                victim_money * percentage
            )

            stolen = max(
                1,
                stolen
            )

            stolen = min(
                stolen,
                MAX_STEAL,
                victim_money
            )

            victim["money"] -= stolen
            robber["money"] += stolen

            robber["wins"] = (
                robber.get(
                    "wins",
                    0
                ) + 1
            )

            guardar_economia(
                data
            )

            embed = discord.Embed(
                title="🦹・ROBO EXITOSO",
                description=(
                    f"💜 **{ctx.author.mention}** "
                    f"se salió con la suya.\n\n"

                    f"🎯 Víctima: "
                    f"**{usuario.display_name}**\n\n"

                    f"💵 Dinero robado: "
                    f"**${format_money(stolen)}**\n\n"

                    f"💰 Tu nuevo saldo: "
                    f"**${format_money(robber['money'])}**"
                ),
                color=PURPLE
            )

            embed.set_thumbnail(
                url=ctx.author.display_avatar.url
            )

            embed.set_footer(
                text="Sistema de economía • Robos"
            )

            await ctx.send(
                embed=embed
            )

        # ====================================================
        # FALLÓ
        # ====================================================

        else:

            # Multa proporcional al dinero del ladrón
            if robber_money > 0:

                fine_percent = random.uniform(
                    0.05,
                    0.15
                )

                fine = int(
                    robber_money
                    * fine_percent
                )

                fine = max(
                    50,
                    fine
                )

                fine = min(
                    fine,
                    MAX_FINE,
                    robber_money
                )

            else:

                fine = 0

            robber["money"] -= fine

            robber["losses"] = (
                robber.get(
                    "losses",
                    0
                ) + 1
            )

            guardar_economia(
                data
            )

            descriptions = [

                (
                    f"🚨 **{usuario.display_name}** "
                    "te descubrió intentando robar."
                ),

                (
                    "🚔 La policía llegó justo a tiempo."
                ),

                (
                    "💀 Te descubrieron con las manos "
                    "en la masa."
                ),

                (
                    "🚨 El robo salió mal."
                ),

                (
                    "👮 Te atraparon antes de poder "
                    "llevarte nada."
                )
            ]

            reason = random.choice(
                descriptions
            )

            if fine > 0:

                money_text = (
                    f"💸 Multa: "
                    f"**${format_money(fine)}**\n\n"
                    f"💰 Saldo actual: "
                    f"**${format_money(robber['money'])}**"
                )

            else:

                money_text = (
                    "💸 No tenías suficiente dinero "
                    "para pagar una multa."
                )

            embed = discord.Embed(
                title="🚨・ROBO FALLIDO",
                description=(
                    f"{reason}\n\n"
                    f"{money_text}"
                ),
                color=DARK_PURPLE
            )

            embed.set_thumbnail(
                url=ctx.author.display_avatar.url
            )

            embed.set_footer(
                text="Sistema de economía • Robos"
            )

            await ctx.send(
                embed=embed
            )

    # ========================================================
    # ESTADÍSTICAS DE ROBOS
    # ========================================================

    @commands.hybrid_command(
        name="robostats",
        description="Muestra tus estadísticas de robos."
    )
    async def robostats(
        self,
        ctx
    ):

        data = cargar_economia()

        user = self.get_user(
            data,
            ctx.author.id
        )

        wins = int(
            user.get(
                "wins",
                0
            )
        )

        losses = int(
            user.get(
                "losses",
                0
            )
        )

        total = (
            wins
            + losses
        )

        if total > 0:

            success_rate = (
                wins
                / total
            ) * 100

        else:

            success_rate = 0

        embed = discord.Embed(
            title="🦹・ESTADÍSTICAS DE ROBOS",
            description=(
                f"👤 **{ctx.author.display_name}**\n\n"

                f"🟢 Robos exitosos: "
                f"**{wins}**\n"

                f"🔴 Robos fallidos: "
                f"**{losses}**\n"

                f"🎯 Intentos totales: "
                f"**{total}**\n\n"

                f"📊 Probabilidad histórica: "
                f"**{success_rate:.1f}%**"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=ctx.author.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # AYUDA DEL ROBO
    # ========================================================

    @commands.hybrid_command(
        name="ayudarobo",
        description="Muestra cómo funciona el sistema de robos."
    )
    async def ayudarobo(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="🦹・SISTEMA DE ROBOS",
            description=(
                "Intentá robar dinero de otro usuario "
                "utilizando tu saldo de economía.\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "**🦹 Cómo robar**\n"
                "`s!robar @usuario`\n"
                "`/robar @usuario`\n\n"

                "**🎯 Probabilidad**\n"
                f"Tenés aproximadamente un "
                f"**{int(SUCCESS_CHANCE * 100)}%** "
                "de posibilidades de éxito.\n\n"

                "**💵 Recompensa**\n"
                f"Podés robar entre "
                f"**{int(MIN_PERCENT * 100)}%** y "
                f"**{int(MAX_PERCENT * 100)}%** "
                "del dinero disponible de la víctima.\n\n"

                f"📦 Máximo por robo: "
                f"**${format_money(MAX_STEAL)}**\n\n"

                "**🚨 Si fallás**\n"
                "Podés recibir una multa.\n\n"

                f"⏳ Cooldown: "
                f"**{ROBO_COOLDOWN // 60} minutos**\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "📊 Mirá tus estadísticas con:\n"
                "`s!robostats`"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text="Economía • Sistema de robos"
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Robo(bot)
    )

    print(
        "[ROBO] Cog cargado correctamente."
    )