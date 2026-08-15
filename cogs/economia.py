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

STARTING_MONEY = 1000

DAILY_MIN = 500
DAILY_MAX = 1500

WORK_MIN = 100
WORK_MAX = 500

DAILY_COOLDOWN = 86400
WORK_COOLDOWN = 3600

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)

COIN = "💵"


# ============================================================
# ECONOMÍA
# ============================================================

class Economia(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        os.makedirs(
            DATA_FOLDER,
            exist_ok=True
        )

        # ----------------------------------------------------
        # CREAR JSON AUTOMÁTICAMENTE
        # ----------------------------------------------------

        if not os.path.exists(DATA_FILE):

            self.data = {}

            self.save_data()

        else:

            self.data = self.load_data()

        print(
            "[ECONOMIA] Cog cargado correctamente."
        )

    # ========================================================
    # CARGAR DATA
    # ========================================================

    def load_data(self):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(
                    data,
                    dict
                ):

                    return data

        except Exception as e:

            print(
                f"[ECONOMIA] Error cargando JSON: {e}"
            )

        return {}

    # ========================================================
    # GUARDAR DATA
    # ========================================================

    def save_data(self):

        try:

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            print(
                f"[ECONOMIA] Error guardando JSON: {e}"
            )

    # ========================================================
    # OBTENER USUARIO
    # ========================================================

    def get_user(
        self,
        user_id
    ):

        user_id = str(
            user_id
        )

        if user_id not in self.data:

            self.data[user_id] = {
                "money": STARTING_MONEY,
                "bank": 0,
                "daily": 0,
                "work": 0,
                "wins": 0,
                "losses": 0,
                "inventory": []
            }

            self.save_data()

        return self.data[user_id]

    # ========================================================
    # FORMATO DINERO
    # ========================================================

    def format_money(
        self,
        amount
    ):

        return f"{amount:,}".replace(
            ",",
            "."
        )

    # ========================================================
    # COOLDOWN
    # ========================================================

    def format_time(
        self,
        seconds
    ):

        seconds = int(
            seconds
        )

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        secs = seconds % 60

        if hours > 0:

            return (
                f"{hours}h "
                f"{minutes}m"
            )

        if minutes > 0:

            return (
                f"{minutes}m "
                f"{secs}s"
            )

        return f"{secs}s"

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

        usuario = (
            usuario
            or ctx.author
        )

        data = self.get_user(
            usuario.id
        )

        total = (
            data["money"]
            + data["bank"]
        )

        embed = discord.Embed(
            title="💰・BALANCE",
            description=(
                f"👤 **{usuario.display_name}**\n\n"
                f"{COIN} Dinero: "
                f"**${self.format_money(data['money'])}**\n"
                f"🏦 Banco: "
                f"**${self.format_money(data['bank'])}**\n\n"
                f"💎 Patrimonio: "
                f"**${self.format_money(total)}**"
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

        data = self.get_user(
            ctx.author.id
        )

        now = time.time()

        remaining = (
            data["daily"]
            + DAILY_COOLDOWN
            - now
        )

        if remaining > 0:

            await ctx.send(
                f"⏳ Ya reclamaste tu recompensa.\n"
                f"Volvé en **{self.format_time(remaining)}**."
            )

            return

        reward = random.randint(
            DAILY_MIN,
            DAILY_MAX
        )

        data["money"] += reward
        data["daily"] = now

        self.save_data()

        await ctx.send(
            f"🎁 **DAILY**\n\n"
            f"Recibiste {COIN} "
            f"**${self.format_money(reward)}**."
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

        data = self.get_user(
            ctx.author.id
        )

        now = time.time()

        remaining = (
            data["work"]
            + WORK_COOLDOWN
            - now
        )

        if remaining > 0:

            await ctx.send(
                f"⏳ Ya trabajaste.\n"
                f"Podés volver en "
                f"**{self.format_time(remaining)}**."
            )

            return

        jobs = [
            "programador",
            "repartidor",
            "streamer",
            "diseñador",
            "mecánico",
            "fotógrafo",
            "DJ",
            "barbero"
        ]

        job = random.choice(
            jobs
        )

        reward = random.randint(
            WORK_MIN,
            WORK_MAX
        )

        data["money"] += reward
        data["work"] = now

        self.save_data()

        await ctx.send(
            f"💼 **TRABAJO COMPLETADO**\n\n"
            f"Trabajaste como **{job}**.\n"
            f"Ganaste {COIN} "
            f"**${self.format_money(reward)}**."
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
        cantidad="Cantidad a transferir."
    )
    async def pay(
        self,
        ctx,
        usuario: discord.Member,
        cantidad: app_commands.Range[
            int,
            1,
            1000000000
        ]
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
                f"Saldo: {COIN} "
                f"**${self.format_money(sender['money'])}**"
            )

            return

        sender["money"] -= cantidad
        receiver["money"] += cantidad

        self.save_data()

        await ctx.send(
            f"💸 **TRANSFERENCIA**\n\n"
            f"{ctx.author.mention} → "
            f"{usuario.mention}\n"
            f"{COIN} **${self.format_money(cantidad)}**"
        )

    # ========================================================
    # COINFLIP
    # ========================================================

    @commands.hybrid_command(
        name="coinflip",
        description="Apostá a cara o cruz."
    )
    @app_commands.describe(
        eleccion="Elegí cara o cruz.",
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
        cantidad: app_commands.Range[
            int,
            1,
            1000000000
        ]
    ):

        data = self.get_user(
            ctx.author.id
        )

        if data["money"] < cantidad:

            await ctx.send(
                "❌ No tenés suficiente dinero."
            )

            return

        result = random.choice(
            [
                "cara",
                "cruz"
            ]
        )

        if result == eleccion.value:

            data["money"] += cantidad
            data["wins"] += 1

            message = (
                f"🎉 Ganaste "
                f"**${self.format_money(cantidad)}**."
            )

        else:

            data["money"] -= cantidad
            data["losses"] += 1

            message = (
                f"💀 Perdiste "
                f"**${self.format_money(cantidad)}**."
            )

        self.save_data()

        await ctx.send(
            f"🪙 **COINFLIP**\n\n"
            f"Elegiste: **{eleccion.value}**\n"
            f"Salió: **{result}**\n\n"
            f"{message}"
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
        cantidad: app_commands.Range[
            int,
            1,
            1000000000
        ]
    ):

        data = self.get_user(
            ctx.author.id
        )

        if data["money"] < cantidad:

            await ctx.send(
                "❌ No tenés suficiente dinero."
            )

            return

        player = random.randint(
            1,
            6
        )

        bot_roll = random.randint(
            1,
            6
        )

        if player > bot_roll:

            data["money"] += cantidad
            result = (
                f"🎉 Ganaste "
                f"**${self.format_money(cantidad)}**."
            )

        elif player < bot_roll:

            data["money"] -= cantidad
            result = (
                f"💀 Perdiste "
                f"**${self.format_money(cantidad)}**."
            )

        else:

            result = (
                "🤝 Empate. "
                "No ganaste ni perdiste."
            )

        self.save_data()

        await ctx.send(
            f"🎲 **DICE**\n\n"
            f"👤 Tu dado: **{player}**\n"
            f"🤖 Rival: **{bot_roll}**\n\n"
            f"{result}"
        )

    # ========================================================
    # SLOTS
    # ========================================================

    @commands.hybrid_command(
        name="slots",
        description="Jugá a las tragamonedas."
    )
    @app_commands.describe(
        cantidad="Cantidad apostada."
    )
    async def slots(
        self,
        ctx,
        cantidad: app_commands.Range[
            int,
            1,
            1000000000
        ]
    ):

        data = self.get_user(
            ctx.author.id
        )

        if data["money"] < cantidad:

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

        if (
            result[0]
            == result[1]
            == result[2]
        ):

            reward = cantidad * 5

            data["money"] += reward

            message = (
                f"🎉 **JACKPOT x5**\n"
                f"Ganaste "
                f"**${self.format_money(reward)}**."
            )

        elif (
            result[0] == result[1]
            or result[1] == result[2]
            or result[0] == result[2]
        ):

            reward = cantidad * 2

            data["money"] += reward

            message = (
                f"✨ **DOS IGUALES**\n"
                f"Ganaste "
                f"**${self.format_money(reward)}**."
            )

        else:

            data["money"] -= cantidad

            message = (
                f"💀 No salió ninguna combinación.\n"
                f"Perdiste "
                f"**${self.format_money(cantidad)}**."
            )

        self.save_data()

        await ctx.send(
            f"🎰 **SLOTS**\n\n"
            f"┃ {' ┃ '.join(result)} ┃\n\n"
            f"{message}"
        )

    # ========================================================
    # GUESS
    # ========================================================

    @commands.hybrid_command(
        name="guess",
        description="Adiviná un número del 1 al 10."
    )
    @app_commands.describe(
        numero="Número del 1 al 10.",
        cantidad="Cantidad apostada."
    )
    async def guess(
        self,
        ctx,
        numero: app_commands.Range[
            int,
            1,
            10
        ],
        cantidad: app_commands.Range[
            int,
            1,
            1000000000
        ]
    ):

        data = self.get_user(
            ctx.author.id
        )

        if data["money"] < cantidad:

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

            data["money"] += reward

            message = (
                f"🎉 ¡Acertaste!\n"
                f"El número era **{number}**.\n"
                f"Ganaste "
                f"**${self.format_money(reward)}**."
            )

        else:

            data["money"] -= cantidad

            message = (
                f"❌ Fallaste.\n"
                f"El número era **{number}**.\n"
                f"Perdiste "
                f"**${self.format_money(cantidad)}**."
            )

        self.save_data()

        await ctx.send(
            f"🔢 **GUESS**\n\n"
            f"{message}"
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
                "📊 Todavía no hay usuarios."
            )

            return

        ranking = []

        for user_id, data in self.data.items():

            total = (
                data.get(
                    "money",
                    0
                )
                + data.get(
                    "bank",
                    0
                )
            )

            ranking.append(
                (
                    int(user_id),
                    total
                )
            )

        ranking.sort(
            key=lambda item: item[1],
            reverse=True
        )

        description = ""

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }

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

            name = (
                member.display_name
                if member
                else f"Usuario {user_id}"
            )

            medal = medals.get(
                position,
                f"**#{position}**"
            )

            description += (
                f"{medal} **{name}** — "
                f"{COIN} **${self.format_money(total)}**\n"
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
    # PANEL DE ECONOMÍA
    # ========================================================

    @commands.hybrid_command(
        name="economia",
        description="Abre el panel de economía y ayuda."
    )
    async def economia(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="💰・ECONOMÍA",
            description=(
                "Bienvenido al sistema de economía de **Band Arg**.\n\n"
                "Usá los botones de abajo para ver "
                "los comandos y aprender a utilizarlos.\n\n"
                "💵 **Economía**\n"
                "🎮 **Juegos**\n"
                "🏆 **Ranking**\n"
                "❓ **Ayuda**"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text="Economía • Band Arg"
        )

        await ctx.send(
            embed=embed,
            view=EconomyView()
        )


# ============================================================
# VIEW
# ============================================================

class EconomyView(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=300
        )

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
        interaction,
        button
    ):

        embed = discord.Embed(
            title="💰・COMANDOS DE ECONOMÍA",
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
        interaction,
        button
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

                "⚠️ Podés ganar o perder dinero."
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
        interaction,
        button
    ):

        embed = discord.Embed(
            title="🏆・RANKING",
            description=(
                "`s!leaderboard`\n\n"
                "Muestra los usuarios más ricos "
                "del servidor."
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
        interaction,
        button
    ):

        embed = discord.Embed(
            title="❓・¿CÓMO SE USA?",
            description=(
                "Todos los comandos funcionan con "
                "`s!` y `/`.\n\n"

                "**Ejemplo:**\n"
                "`s!balance`\n"
                "`/balance`\n\n"

                "**🎰 Apostar:**\n"
                "`s!slots 500`\n\n"

                "**💸 Pagar:**\n"
                "`s!pay @usuario 500`\n\n"

                "**🏆 Ranking:**\n"
                "`s!leaderboard`\n\n"

                "⚠️ Los juegos pueden hacerte ganar "
                "o perder dinero."
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