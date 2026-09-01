import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DB_FILE = DATA_FOLDER / "panelstats.db"


# ============================================================
# BASE DE DATOS
# ============================================================

def conectar():

    DATA_FOLDER.mkdir(
        exist_ok=True
    )

    db = sqlite3.connect(
        DB_FILE
    )

    db.row_factory = sqlite3.Row

    return db


def preparar_base():

    with conectar() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                guild_name TEXT NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)

        db.commit()


# ============================================================
# COG
# ============================================================

class PanelStats(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        preparar_base()

        print(
            "📊 PanelStats iniciado correctamente."
        )

    # ========================================================
    # REGISTRAR CLIC
    # ========================================================

    def registrar_click(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return

        ahora = datetime.now(
            timezone.utc
        ).strftime(
            "%d/%m/%Y %H:%M:%S UTC"
        )

        with conectar() as db:

            db.execute(
                """
                INSERT INTO clicks (
                    guild_id,
                    guild_name,
                    channel_id,
                    channel_name,
                    user_id,
                    username,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction.guild.id,
                    interaction.guild.name,
                    interaction.channel.id,
                    getattr(
                        interaction.channel,
                        "name",
                        "desconocido"
                    ),
                    interaction.user.id,
                    str(interaction.user),
                    ahora
                )
            )

            db.commit()

    # ========================================================
    # OBTENER CLICKS
    # ========================================================

    def obtener_clicks(
        self,
        guild_id,
        limite=10
    ):

        with conectar() as db:

            return db.execute(
                """
                SELECT *
                FROM clicks
                WHERE guild_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    guild_id,
                    limite
                )
            ).fetchall()

    # ========================================================
    # TOTAL
    # ========================================================

    def obtener_total(
        self,
        guild_id
    ):

        with conectar() as db:

            resultado = db.execute(
                """
                SELECT COUNT(*) AS total
                FROM clicks
                WHERE guild_id = ?
                """,
                (
                    guild_id,
                )
            ).fetchone()

            return resultado["total"]

    # ========================================================
    # /panelstats
    # ========================================================

    @app_commands.command(
        name="panelstats",
        description="Muestra quién apretó el botón del panel."
    )
    @app_commands.describe(
        cantidad="Cantidad de registros que querés mostrar."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def panelstats(
        self,
        interaction: discord.Interaction,
        cantidad: int = 10
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Necesitás permisos de administrador.",
                ephemeral=True
            )

        cantidad = max(
            1,
            min(cantidad, 25)
        )

        registros = self.obtener_clicks(
            interaction.guild.id,
            cantidad
        )

        total = self.obtener_total(
            interaction.guild.id
        )

        if not registros:

            return await interaction.response.send_message(
                "📊 Todavía no hay clics registrados.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="📊 Estadísticas del panel",
            description=(
                f"🔘 **Clics totales:** {total}\n"
                f"📋 **Mostrando:** {len(registros)}"
            ),
            color=discord.Color.from_rgb(
                255,
                115,
                0
            )
        )

        for registro in registros:

            usuario = (
                f"<@{registro['user_id']}>"
            )

            canal = (
                f"<#{registro['channel_id']}>"
            )

            valor = (
                f"👤 **Usuario:** {usuario}\n"
                f"🆔 `{registro['user_id']}`\n"
                f"🕐 **Fecha:** {registro['timestamp']}\n"
                f"📍 **Canal:** {canal}\n"
                f"🌐 **Servidor:** {registro['guild_name']}"
            )

            embed.add_field(
                name="🔘 Clic registrado",
                value=valor,
                inline=False
            )

        embed.set_footer(
            text="PanelStats • Últimos registros"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /panelstats_total
    # ========================================================

    @app_commands.command(
        name="panelstats_total",
        description="Muestra la cantidad total de clics."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def panelstats_total(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Necesitás permisos de administrador.",
                ephemeral=True
            )

        total = self.obtener_total(
            interaction.guild.id
        )

        await interaction.response.send_message(
            f"📊 **Clics totales:** `{total}`",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        PanelStats(bot)
    )
