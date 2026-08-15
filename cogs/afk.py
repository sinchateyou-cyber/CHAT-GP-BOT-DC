import discord
from discord.ext import commands
from discord import app_commands

import os
import json
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(
    DATA_FOLDER,
    "afk.json"
)

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)


# ============================================================
# COG AFK
# ============================================================

class AFK(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        os.makedirs(
            DATA_FOLDER,
            exist_ok=True
        )

        self.data = self.load_data()

        # Usuarios a los que ya se les avisó
        # en una determinada conversación/mensaje.
        self.notified = set()

        print(
            "[AFK] Cog cargado correctamente."
        )

    # ========================================================
    # CARGAR DATA
    # ========================================================

    def load_data(self):

        if not os.path.exists(DATA_FILE):

            return {}

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
                f"[AFK] Error cargando JSON: {e}"
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
                f"[AFK] Error guardando JSON: {e}"
            )

    # ========================================================
    # FORMATO TIEMPO
    # ========================================================

    def format_duration(
        self,
        seconds
    ):

        seconds = int(
            seconds
        )

        days = seconds // 86400

        seconds %= 86400

        hours = seconds // 3600

        seconds %= 3600

        minutes = seconds // 60

        seconds %= 60

        parts = []

        if days:
            parts.append(
                f"{days}d"
            )

        if hours:
            parts.append(
                f"{hours}h"
            )

        if minutes:
            parts.append(
                f"{minutes}m"
            )

        if seconds and len(parts) < 2:
            parts.append(
                f"{seconds}s"
            )

        if not parts:

            return "unos segundos"

        return " ".join(
            parts
        )

    # ========================================================
    # OBTENER AFK
    # ========================================================

    def get_afk(
        self,
        user_id
    ):

        return self.data.get(
            str(user_id)
        )

    # ========================================================
    # ELIMINAR AFK
    # ========================================================

    def remove_afk(
        self,
        user_id
    ):

        user_id = str(
            user_id
        )

        if user_id in self.data:

            del self.data[user_id]

            self.save_data()

    # ========================================================
    # COMANDO AFK
    # ========================================================

    @commands.hybrid_command(
        name="afk",
        description="Ponete AFK con un motivo."
    )
    @app_commands.describe(
        motivo="Motivo por el que te vas AFK."
    )
    async def afk(
        self,
        ctx,
        *,
        motivo: str = "No especificado"
    ):

        user_id = str(
            ctx.author.id
        )

        now = time.time()

        # ----------------------------------------------------
        # SI YA ESTABA AFK
        # ----------------------------------------------------

        if user_id in self.data:

            self.data[user_id]["reason"] = motivo
            self.data[user_id]["since"] = now

        # ----------------------------------------------------
        # NUEVO AFK
        # ----------------------------------------------------

        else:

            self.data[user_id] = {
                "reason": motivo,
                "since": now
            }

        self.save_data()

        embed = discord.Embed(
            title="💤・AFK ACTIVADO",
            description=(
                f"{ctx.author.mention} ahora está AFK.\n\n"
                f"💭 **Motivo:** {motivo}"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=ctx.author.display_avatar.url
        )

        embed.set_footer(
            text="Te avisaré cuando alguien te mencione."
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # LISTENER DE MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        # ----------------------------------------------------
        # IGNORAR BOTS
        # ----------------------------------------------------

        if message.author.bot:

            return

        # ----------------------------------------------------
        # ELIMINAR AFK AL VOLVER
        # ----------------------------------------------------

        author_id = str(
            message.author.id
        )

        if author_id in self.data:

            afk_data = self.data[
                author_id
            ]

            since = afk_data.get(
                "since",
                time.time()
            )

            duration = (
                time.time()
                - since
            )

            reason = afk_data.get(
                "reason",
                "No especificado"
            )

            del self.data[
                author_id
            ]

            self.save_data()

            embed = discord.Embed(
                title="👋・BIENVENIDO DE VUELTA",
                description=(
                    f"{message.author.mention} "
                    f"ya no está AFK.\n\n"
                    f"⏱️ Estuviste AFK durante "
                    f"**{self.format_duration(duration)}**.\n"
                    f"💭 Motivo: **{reason}**"
                ),
                color=PURPLE
            )

            await message.channel.send(
                embed=embed,
                delete_after=8
            )

        # ----------------------------------------------------
        # BUSCAR MENCIONES
        # ----------------------------------------------------

        if not message.mentions:

            return

        mentioned_afk = []

        for member in message.mentions:

            if member.bot:

                continue

            user_id = str(
                member.id
            )

            if user_id not in self.data:

                continue

            mentioned_afk.append(
                (
                    member,
                    self.data[user_id]
                )
            )

        # ----------------------------------------------------
        # NO HAY AFK
        # ----------------------------------------------------

        if not mentioned_afk:

            return

        # ----------------------------------------------------
        # AVISAR
        # ----------------------------------------------------

        for member, afk_data in mentioned_afk:

            reason = afk_data.get(
                "reason",
                "No especificado"
            )

            since = afk_data.get(
                "since",
                time.time()
            )

            duration = (
                time.time()
                - since
            )

            embed = discord.Embed(
                title="💤・USUARIO AFK",
                description=(
                    f"{member.mention} está AFK.\n\n"
                    f"💭 **Motivo:** {reason}\n"
                    f"⏱️ **Desde hace:** "
                    f"{self.format_duration(duration)}"
                ),
                color=PURPLE
            )

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

            await message.channel.send(
                embed=embed,
                delete_after=10
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        AFK(bot)
    )

    print(
        "[AFK] Sistema AFK activado."
    )