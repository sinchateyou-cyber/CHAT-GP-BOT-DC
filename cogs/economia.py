# cogs/economia.py

import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import time
import asyncio


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "economia.json")

COIN = "💵"
STARTING_MONEY = 1000

DAILY_REWARD = (500, 1500)
WORK_REWARD = (100, 500)

DAILY_COOLDOWN = 86400
WORK_COOLDOWN = 3600

PURPLE = discord.Color.from_rgb(115, 55, 210)


# ============================================================
# ECONOMÍA
# ============================================================

class Economia(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.save_data({})

        self.data = self.load_data()

        print("[ECONOMIA] Cog cargado.")

    # ========================================================
    # DATA
    # ========================================================

    def load_data(self):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                if isinstance(data, dict):
                    return data

        except Exception as e:

            print(
                f"[ECONOMIA] Error cargando datos: {e}"
            )

        return {}

    # ========================================================

    def save_data(self):

        try:

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            print(
                f"[ECONOMIA] Error guardando datos: {e}"
            )

    # ========================================================
    # USUARIO
    # ========================================================

    def get_user(self, user_id):

        user_id = str(user_id)

        if user_id not in self.data:

            self.data[user_id] = {
                "money": STARTING_MONEY,
                "bank": 0,
                "inventory": [],
                "daily": 0,
                "work": 0,
                "wins": 0,
                "losses": 0
            }

            self.save_data()

        return self.data[user_id]

    # ========================================================
    # FORMATO DINERO
    # ========================================================

    def money(self, amount):

        return f"{amount:,}".replace(",", ".")

    # ========================================================
    # TIEMPO
    # ========================================================

    def cooldown_text(self, remaining):

        remaining = int(remaining)

        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60

        if hours:
            return f"{hours}h {minutes}m"

        if minutes:
            return f"{minutes}m {seconds}s"

        return f"{seconds}s"

    # ========================================================
    # BALANCE
    # ========================================================

    @commands.hybrid_command(
        name="balance",
        description="Muestra tu dinero."
    )
    @app_commands.describe(
        usuario="Usuario que querés consultar."
    )
    async def balance(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        usuario = usuario or ctx.author

        user = self.get_user(
            usuario.id
        )

        embed = discord.Embed(
            title="💰・BALANCE",
            description=(
                f"💳 **{usuario.display_name}**\n\n"
                f"{COIN} Dinero: "
                f"**${self.money(user['money'])}**\n"
                f"🏦 Banco: "
                f"**${self.money(user['bank'])}**\n\n"
                f"💎 Patrimonio total: "
                f"**${self.money(user['money'] + user['bank'])}**"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # DAILY
    # ========================================================

    @commands.hybrid_command(
        name="daily",
        description="Reclama tu recompensa diaria."
    )
    async def daily(
        self,
        ctx
    ):

        user = self.get_user(
            ctx.author.id
        )

        now = time.time()

        remaining = (
            user["daily"]
            + DAILY_COOLDOWN
            - now
        )

        if remaining > 0:

            await ctx.send(
                f"⏳ Ya reclamaste tu recompensa. "
                f"Volvé en **{self.cooldown_text(remaining)}**."
            )

            return

        reward = random.randint(
            DAILY_REWARD[0],
            DAILY_REWARD[1]
        )

        user["money"] += reward
        user["daily"] = now

        self.save_data()

        await ctx.send(
            f"🎁 **Recompensa diaria**\n\n"
            f"Recibiste {COIN} **${self.money(reward)}**."
        )

    # ========================================================
    # WORK
    # ========================================================

    @commands.hybrid_command(
        name="work",
        description="Trabajá para ganar dinero."
    )
    async def work(
        self,
        ctx
    ):

        user = self.get_user(
            ctx.author.id
        )

        now = time.time()

        remaining = (
            user["work"]
            + WORK_COOLDOWN
            - now
        )

        if remaining > 0:

            await ctx.send(
                f"⏳ Ya trabajaste recientemente. "
                f"Podés volver a trabajar en "
                f"**{self.cooldown_text(remaining)}**."
            )

            return

        jobs = [
            "programador",
            "repartidor",
            "streamer",
            "diseñador",
            "barbero",
            "mecánico",
            "fotógrafo",
            "DJ"
        ]

        job = random.choice(jobs)

        reward = random.randint(
            WORK_REWARD[0],
            WORK_REWARD[1]
        )

        user["money"] += reward
        user["work"] = now

        self.save_data()

        await ctx.send(
            f"💼 **Trabajo completado**\n\n"
            f"Trabajaste como **{job}**.\n"
            f"Ganaste {COIN} **${self.money(reward)}**."
        )

    # ========================================================
    # PAY
    # ========================================================

    @commands.hybrid_command(
        name="pay",
        description="Transferí dinero a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario que recibirá el dinero.",
        cantidad="Cantidad de dinero."
    )
    async def pay(
        self,
        ctx,
        usuario: discord.Member,
        cantidad: app_commands.Range[int, 1, 1000000000]
    ):

        if usuario.bot:

            await ctx.send(
                "❌ No podés pagarle a un bot."
            )

            return

        if usuario.id == ctx.author.id:

            await ctx.send(
                "❌ No podés pagarte a vos mismo."
            )

            return

        sender = self.get_user(
            ctx.author.id
        )

        receiver = self.get_user(
            usuario.id
        )

        if sender["money"] < cantidad:

            await ctx.send(
                f"❌ No tenés suficiente dinero.\n"
                f"Tu saldo: {COIN} **${self.money(sender['money'])}**"
            )

            return

        sender["money"] -= cantidad
        receiver["money"] += cantidad

        self.save_data()

        await ctx.send(
            f"💸 **Transferencia realizada**\n\n"
            f"{ctx.author.mention} → {usuario.mention}\n"
            f"{COIN} **${self.money(cantidad)}**"
        )

    # ========================================================
    # COINFLIP
    # ========================================================

    @commands.hybrid_command(
        name="coinflip",
        description="Apostá a cara o cruz."
    )
    @app_commands.describe(
        eleccion="cara o cruz",
        cantidad="Cantidad apostada."
    )
    @app_commands.choices(
        eleccion=[
            app_commands.Choice(
                name="Cara",
                value="cara"
            ),
            app_commands.Choice(
                name="Cruz",
                value="cruz"
            )
        ]
    )
    async def coinflip(
        self,
        ctx,
        eleccion: app_commands.Choice[str],
        cantidad: app_commands.Range[int, 1, 1000000000]
    ):

        user = self.get_user(
            ctx.author.id
        )

        if user["money"] < cantidad:

            await ctx.send(
                "❌ No tenés suficiente dinero."
            )

            return

        result = random.choice(
            ["cara", "cruz"]
        )

        if result == eleccion.value:

            user["money"] += cantidad
            user["wins"] += 1

            resultado = (
                f"🎉 Ganaste **${self.money(cantidad)}**."
            )

        else:

            user["money"] -= cantidad
            user["losses"] += 1

            resultado = (
                f"💀 Perdiste **${self.money(cantidad)}**."
            )

        self.save_data()

        await ctx.send(
            f"🪙 **COINFLIP**\n\n"
            f"Tu elección: **{eleccion.value}**\n"
            f"Salió: **{result}**\n\n"
            f"{resultado}"
        )

    # ========================================================
    # DICE
    # ========================================================

    @commands.hybrid_command(
        name="dice",
        description="Tirá los dados y apostá."
    )
    @app_commands.describe(
        cantidad="Cantidad apostada."
    )
    async def dice(
        self,
        ctx,
        cantidad: app_commands.Range[int, 1, 1000000000]
    ):

        user = self.get_user(
            ctx.author.id
        )

        if user["money"] < cantidad:

            await ctx.send(
                "❌ No tenés suficiente dinero."
            )

            return

        player = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if player > bot_roll:

            user["money"] += cantidad

            result = (
                f"🎉 Ganaste **${self.money(cantidad)}**."
            )

        elif player < bot_roll:

            user["money"] -= cantidad

            result = (
                f"💀 Perdiste **${self.money(cantidad)}**."
            )

        else:

            result = (
                "🤝 Empate. No ganaste ni perdiste."
            )

        self.save_data()

        await ctx.send(
            f"🎲 **DICE**\n\n"
            f"👤 Tu dado: **{player}**\n"
            f"🤖 Dado rival: **{bot_roll}**\n\n"
            f"{result}"
        )

    # ========================================================
    # SLOTS
    # ========================================================

    @commands.hybrid_command(
        name="slots",
        description="Jugá a la tragamonedas."
    )
    @app_commands.describe(
        cantidad="Cantidad apostada."
    )
    async def slots(
        self,
        ctx,
        cantidad: app_commands.Range[int, 1, 1000000000]
    ):

        user = self.get_user(
            ctx.author.id
        )

        if user["money"] < cantidad:

            await ctx.send(
                "❌ No tenés suficiente dinero."
            )

            return

        symbols = [
            "🍒",
            "🍋",
            "🍉",
            "⭐",
            "💎",
            "7️⃣"
        ]

        result = [
            random.choice(symbols),
            random.choice(symbols),
            random.choice(symbols)
        ]

        if result[0] == result[1] == result[2]:

            multiplier = 5

            reward = cantidad * multiplier

            user["money"] += reward

            text = (
                f"🎉 **JACKPOT x{multiplier}!**\n"
                f"Ganaste **${self.money(reward)}**."
            )

        elif (
            result[0] == result[1]
            or result[1] == result[2]
            or result[0] == result[2]
        ):

            reward = cantidad * 2

            user["money"] += reward

            text = (
                f"✨ **Dos iguales!**\n"
                f"Ganaste **${self.money(reward)}**."
            )

        else:

            user["money"] -= cantidad

            text = (
                f"💀 No salió ninguna combinación.\n"
                f"Perdiste **${self.money(cantidad)}**."
            )

        self.save_data()

        await ctx.send(
            f"🎰 **SLOTS**\n\n"
            f"┃ {' ┃ '.join(result)} ┃\n\n"
            f"{text}"
        )

    # ========================================================
    # GUESS
    # ========================================================

    @commands.hybrid_command(
        name="guess",
        description="Adiviná un número del 1 al 10."
    )
    @app_commands.describe(
        numero="Número entre 1 y 10.",
        cantidad="Cantidad apostada."
    )
    async def guess(
        self,
        ctx,
        numero: app_commands.Range[int, 1, 10],
        cantidad: app_commands.Range[int, 1, 1000000000]
    ):

        user = self.get_user(
            ctx.author.id
        )

        if user["money"] < cantidad:

            await ctx.send(
                "❌ No tenés suficiente dinero."
            )

            return

        number = random.randint(
            1,
            10
        )

        if numero == number:

            reward = cantidad * 5

            user["money"] += reward

            text = (
                f"🎉 ¡Acertaste!\n"
                f"El número era **{number}**.\n"
                f"Ganaste **${self.money(reward)}**."
            )

        else:

            user["money"] -= cantidad

            text = (
                f"❌ Fallaste.\n"
                f"El número era **{number}**.\n"
                f"Perdiste **${self.money(cantidad)}**."
            )

        self.save_data()

        await ctx.send(
            f"🔢 **GUESS**\n\n{text}"
        )

    # ========================================================
    # LEADERBOARD
    # ========================================================

    @commands.hybrid_command(
        name="leaderboard",
        description="Muestra el ranking de riqueza."
    )
    async def leaderboard(
        self,
        ctx
    ):

        if not self.data:

            await ctx.send(
                "📊 Todavía no hay usuarios en el ranking."
            )

            return

        ranking = []

        for user_id, data in self.data.items():

            total = (
                data.get("money", 0)
                + data.get("bank", 0)
            )

            ranking.append(
                (
                    int(user_id),
                    total
                )
            )

        ranking.sort(
            key=lambda x: x[1],
            reverse=True
        )

        description = ""

        for position, (
            user_id,
            total
        ) in enumerate(
            ranking[:10],
            start=1
        ):

            member = ctx.guild.get_member(
                user_id
            )

            if member:

                name = member.display_name

            else:

                name = f"Usuario {user_id}"

            medals = {
                1: "🥇",
                2: "🥈",
                3: "🥉"
            }

            medal = medals.get(
                position,
                f"`#{position}`"
            )

            description += (
                f"{medal} **{name}** — "
                f"{COIN} **${self.money(total)}**\n"
            )

        embed = discord.Embed(
            title="🏆・RANKING DE RIQUEZA",
            description=description,
            color=PURPLE
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # AYUDA
    # ========================================================

    @commands.hybrid_command(
        name="economia",
        description="Abre el centro de ayuda de economía."
    )
    async def economia(
        self,
        ctx
    ):

        view = EconomyHelpView(
            self
        )

        embed = discord.Embed(
            title="💰・CENTRO DE ECONOMÍA",
            description=(
                "Bienvenido al sistema de economía.\n\n"
                "Usá los botones de abajo para aprender "
                "cómo funciona cada sección.\n\n"
                "💵 **Economía**\n"
                "🎮 **Juegos**\n"
                "🏆 **Ranking**\n"
                "❓ **Ayuda**"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text="Sistema de economía"
        )

        await ctx.send(
            embed=embed,
            view=view
        )


# ============================================================
# PANEL DE AYUDA
# ============================================================

class EconomyHelpView(
    discord.ui.View
):

    def __init__(
        self,
        economy
    ):

        super().__init__(
            timeout=300
        )

        self.economy = economy

    # ========================================================
    # ECONOMÍA
    # ========================================================

    @discord.ui.button(
        label="Economía",
        emoji="💰",
        style=discord.ButtonStyle.primary
    )
    async def economy_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="💰・ECONOMÍA",
            description=(
                "**💵 Balance**\n"
                "`s!balance`\n"
                "Muestra tu dinero.\n\n"

                "**🎁 Daily**\n"
                "`s!daily`\n"
                "Reclamá tu recompensa diaria.\n\n"

                "**💼 Work**\n"
                "`s!work`\n"
                "Trabajá para ganar dinero.\n\n"

                "**💸 Pay**\n"
                "`s!pay @usuario 500`\n"
                "Transferí dinero."
            ),
            color=PURPLE
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # JUEGOS
    # ========================================================

    @discord.ui.button(
        label="Juegos",
        emoji="🎮",
        style=discord.ButtonStyle.success
    )
    async def games_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🎮・JUEGOS",
            description=(
                "**🪙 Coinflip**\n"
                "`s!coinflip cara 500`\n\n"

                "**🎰 Slots**\n"
                "`s!slots 500`\n\n"

                "**🎲 Dice**\n"
                "`s!dice 500`\n\n"

                "**🔢 Guess**\n"
                "`s!guess 7 500`\n\n"

                "⚠️ En los juegos podés ganar **o perder** dinero."
            ),
            color=PURPLE
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # RANKING
    # ========================================================

    @discord.ui.button(
        label="Ranking",
        emoji="🏆",
        style=discord.ButtonStyle.secondary
    )
    async def ranking_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="🏆・RANKING",
            description=(
                "`s!leaderboard`\n\n"
                "Muestra los usuarios con mayor "
                "cantidad de dinero del servidor."
            ),
            color=PURPLE
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # AYUDA
    # ========================================================

    @discord.ui.button(
        label="Ayuda",
        emoji="❓",
        style=discord.ButtonStyle.danger
    )
    async def help_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = discord.Embed(
            title="❓・¿CÓMO SE USA?",
            description=(
                "Podés usar los comandos con `s!` "
                "o con `/`.\n\n"

                "**Ejemplo:**\n"
                "`s!balance`\n"
                "`/balance`\n\n"

                "**Para apostar:**\n"
                "`s!slots 500`\n\n"

                "**Para pagar:**\n"
                "`s!pay @usuario 500`\n\n"

                "**Para ver todos los comandos:**\n"
                "`s!help`"
            ),
            color=PURPLE
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Economia(bot)
    )