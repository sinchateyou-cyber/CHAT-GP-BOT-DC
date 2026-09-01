```python
# cogs/vcstats.py

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
DB_FILE = DATA_FOLDER / "vc_stats.db"


# ============================================================
# BASE DE DATOS
# ============================================================

def conectar():

    DATA_FOLDER.mkdir(
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


def preparar_base():

    with conectar() as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS vc_stats (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                total_seconds REAL DEFAULT 0,
                sessions INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS vc_channels (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_name TEXT NOT NULL,
                seconds REAL DEFAULT 0,
                PRIMARY KEY (
                    guild_id,
                    user_id,
                    channel_id
                )
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS vc_daily (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                seconds REAL DEFAULT 0,
                PRIMARY KEY (
                    guild_id,
                    user_id,
                    date
                )
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS vc_weekly (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                week TEXT NOT NULL,
                seconds REAL DEFAULT 0,
                PRIMARY KEY (
                    guild_id,
                    user_id,
                    week
                )
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS vc_sessions (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                started_at REAL NOT NULL,
                channel_id INTEGER NOT NULL,
                channel_name TEXT NOT NULL,
                PRIMARY KEY (
                    guild_id,
                    user_id
                )
            )
        """)


# ============================================================
# UTILIDADES
# ============================================================

def timestamp():

    return datetime.now(
        timezone.utc
    ).timestamp()


def fecha_actual():

    return datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")


def semana_actual():

    dt = datetime.now(
        timezone.utc
    )

    year, week, _ = dt.isocalendar()

    return f"{year}-W{week:02d}"


def formatear_tiempo(segundos):

    segundos = int(
        max(0, segundos)
    )

    dias = segundos // 86400
    segundos %= 86400

    horas = segundos // 3600
    segundos %= 3600

    minutos = segundos // 60
    segundos %= 60

    partes = []

    if dias:
        partes.append(
            f"{dias}d"
        )

    if horas:
        partes.append(
            f"{horas}h"
        )

    if minutos:
        partes.append(
            f"{minutos}m"
        )

    if not partes:

        partes.append(
            f"{segundos}s"
        )

    return " ".join(partes)


# ============================================================
# COG
# ============================================================

class VCStats(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        preparar_base()

        print(
            "🎙️ VCStats SQLite iniciado."
        )

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        # Recuperar sesiones de personas
        # que estaban en VC cuando el bot se reinició.

        for guild in self.bot.guilds:

            for channel in guild.voice_channels:

                for member in channel.members:

                    if member.bot:
                        continue

                    self.recuperar_sesion(
                        member,
                        channel
                    )

    # ========================================================
    # RECUPERAR SESIÓN
    # ========================================================

    def recuperar_sesion(
        self,
        member,
        channel
    ):

        with conectar() as db:

            existente = db.execute(
                """
                SELECT *
                FROM vc_sessions
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    member.guild.id,
                    member.id
                )
            ).fetchone()

            if existente:
                return

            db.execute(
                """
                INSERT INTO vc_sessions (
                    guild_id,
                    user_id,
                    started_at,
                    channel_id,
                    channel_name
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    member.guild.id,
                    member.id,
                    timestamp(),
                    channel.id,
                    channel.name
                )
            )

        print(
            f"🔄 Sesión recuperada: "
            f"{member} → {channel.name}"
        )

    # ========================================================
    # VOICE STATE
    # ========================================================

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):

        if member.bot:
            return

        # ----------------------------------------------------
        # ENTRÓ
        # ----------------------------------------------------

        if (
            before.channel is None
            and after.channel is not None
        ):

            self.iniciar_sesion(
                member,
                after.channel
            )

            return

        # ----------------------------------------------------
        # SALIÓ
        # ----------------------------------------------------

        if (
            before.channel is not None
            and after.channel is None
        ):

            self.finalizar_sesion(
                member
            )

            return

        # ----------------------------------------------------
        # CAMBIÓ DE CANAL
        # ----------------------------------------------------

        if (
            before.channel is not None
            and after.channel is not None
            and before.channel.id != after.channel.id
        ):

            self.finalizar_sesion(
                member
            )

            self.iniciar_sesion(
                member,
                after.channel
            )

    # ========================================================
    # INICIAR SESIÓN
    # ========================================================

    def iniciar_sesion(
        self,
        member,
        channel
    ):

        with conectar() as db:

            db.execute(
                """
                INSERT OR REPLACE INTO vc_sessions (
                    guild_id,
                    user_id,
                    started_at,
                    channel_id,
                    channel_name
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    member.guild.id,
                    member.id,
                    timestamp(),
                    channel.id,
                    channel.name
                )
            )

        print(
            f"🎙️ {member} entró a "
            f"{channel.name}"
        )

    # ========================================================
    # FINALIZAR SESIÓN
    # ========================================================

    def finalizar_sesion(
        self,
        member
    ):

        with conectar() as db:

            session = db.execute(
                """
                SELECT *
                FROM vc_sessions
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    member.guild.id,
                    member.id
                )
            ).fetchone()

            if not session:
                return

            fin = timestamp()

            duracion = max(
                0,
                fin - session["started_at"]
            )

            guild_id = member.guild.id
            user_id = member.id
            channel_id = session["channel_id"]
            channel_name = session["channel_name"]

            # ------------------------------------------------
            # ESTADÍSTICAS GENERALES
            # ------------------------------------------------

            db.execute(
                """
                INSERT INTO vc_stats (
                    guild_id,
                    user_id,
                    total_seconds,
                    sessions
                )
                VALUES (?, ?, ?, 1)

                ON CONFLICT(guild_id, user_id)
                DO UPDATE SET
                    total_seconds =
                        total_seconds + excluded.total_seconds,
                    sessions =
                        sessions + 1
                """,
                (
                    guild_id,
                    user_id,
                    duracion
                )
            )

            # ------------------------------------------------
            # CANAL
            # ------------------------------------------------

            db.execute(
                """
                INSERT INTO vc_channels (
                    guild_id,
                    user_id,
                    channel_id,
                    channel_name,
                    seconds
                )
                VALUES (?, ?, ?, ?, ?)

                ON CONFLICT(
                    guild_id,
                    user_id,
                    channel_id
                )
                DO UPDATE SET
                    seconds =
                        seconds + excluded.seconds,
                    channel_name =
                        excluded.channel_name
                """,
                (
                    guild_id,
                    user_id,
                    channel_id,
                    channel_name,
                    duracion
                )
            )

            # ------------------------------------------------
            # DÍA
            # ------------------------------------------------

            db.execute(
                """
                INSERT INTO vc_daily (
                    guild_id,
                    user_id,
                    date,
                    seconds
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(
                    guild_id,
                    user_id,
                    date
                )
                DO UPDATE SET
                    seconds =
                        seconds + excluded.seconds
                """,
                (
                    guild_id,
                    user_id,
                    fecha_actual(),
                    duracion
                )
            )

            # ------------------------------------------------
            # SEMANA
            # ------------------------------------------------

            db.execute(
                """
                INSERT INTO vc_weekly (
                    guild_id,
                    user_id,
                    week,
                    seconds
                )
                VALUES (?, ?, ?, ?)

                ON CONFLICT(
                    guild_id,
                    user_id,
                    week
                )
                DO UPDATE SET
                    seconds =
                        seconds + excluded.seconds
                """,
                (
                    guild_id,
                    user_id,
                    semana_actual(),
                    duracion
                )
            )

            # ------------------------------------------------
            # ELIMINAR SESIÓN ACTUAL
            # ------------------------------------------------

            db.execute(
                """
                DELETE FROM vc_sessions
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    guild_id,
                    user_id
                )
            )

        print(
            f"🎙️ {member} salió de VC "
            f"({formatear_tiempo(duracion)})"
        )

    # ========================================================
    # OBTENER ESTADÍSTICAS
    # ========================================================

    def obtener_stats(
        self,
        guild_id,
        user_id
    ):

        with conectar() as db:

            stats = db.execute(
                """
                SELECT *
                FROM vc_stats
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    guild_id,
                    user_id
                )
            ).fetchone()

            if not stats:

                total = 0
                sesiones = 0

            else:

                total = stats["total_seconds"]
                sesiones = stats["sessions"]

            # ------------------------------------------------
            # SESIÓN ACTUAL
            # ------------------------------------------------

            session = db.execute(
                """
                SELECT *
                FROM vc_sessions
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    guild_id,
                    user_id
                )
            ).fetchone()

            canal_actual = None

            if session:

                total += max(
                    0,
                    timestamp() - session["started_at"]
                )

                canal_actual = session[
                    "channel_name"
                ]

            # ------------------------------------------------
            # HOY
            # ------------------------------------------------

            daily = db.execute(
                """
                SELECT seconds
                FROM vc_daily
                WHERE guild_id = ?
                AND user_id = ?
                AND date = ?
                """,
                (
                    guild_id,
                    user_id,
                    fecha_actual()
                )
            ).fetchone()

            hoy = (
                daily["seconds"]
                if daily
                else 0
            )

            # ------------------------------------------------
            # SEMANA
            # ------------------------------------------------

            weekly = db.execute(
                """
                SELECT seconds
                FROM vc_weekly
                WHERE guild_id = ?
                AND user_id = ?
                AND week = ?
                """,
                (
                    guild_id,
                    user_id,
                    semana_actual()
                )
            ).fetchone()

            semana = (
                weekly["seconds"]
                if weekly
                else 0
            )

            # ------------------------------------------------
            # SUMAR SESIÓN ACTUAL A HOY/SEMANA
            # ------------------------------------------------

            if session:

                duracion_actual = max(
                    0,
                    timestamp() - session["started_at"]
                )

                hoy += duracion_actual
                semana += duracion_actual

            # ------------------------------------------------
            # CANAL MÁS USADO
            # ------------------------------------------------

            canal = db.execute(
                """
                SELECT channel_name, seconds
                FROM vc_channels
                WHERE guild_id = ?
                AND user_id = ?
                ORDER BY seconds DESC
                LIMIT 1
                """,
                (
                    guild_id,
                    user_id
                )
            ).fetchone()

        return {
            "total": total,
            "hoy": hoy,
            "semana": semana,
            "sesiones": sesiones,
            "canal": canal,
            "canal_actual": canal_actual
        }

    # ========================================================
    # /VCSTATS
    # ========================================================

    @app_commands.command(
        name="vcstats",
        description="Muestra las horas que pasaste en canales de voz."
    )
    @app_commands.describe(
        usuario="Usuario del que querés ver las estadísticas."
    )
    async def vcstats(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member = None
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        if usuario is None:

            usuario = interaction.user

        stats = self.obtener_stats(
            interaction.guild.id,
            usuario.id
        )

        embed = discord.Embed(
            title="🎙️ Estadísticas de voz",
            description=(
                f"### {usuario.display_name}\n\n"
                f"⏱️ **Tiempo total:** "
                f"{formatear_tiempo(stats['total'])}\n\n"
                f"📅 **Hoy:** "
                f"{formatear_tiempo(stats['hoy'])}\n\n"
                f"📆 **Esta semana:** "
                f"{formatear_tiempo(stats['semana'])}\n\n"
                f"🎧 **Sesiones:** "
                f"{stats['sesiones']}"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        if stats["canal"]:

            embed.add_field(
                name="🏆 Canal más usado",
                value=(
                    f"**{stats['canal']['channel_name']}**\n"
                    f"⏱️ {formatear_tiempo(stats['canal']['seconds'])}"
                ),
                inline=False
            )

        if stats["canal_actual"]:

            embed.add_field(
                name="🟢 Actualmente",
                value=(
                    f"Está en **{stats['canal_actual']}**"
                ),
                inline=False
            )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=interaction.guild.name
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ========================================================
    # /VCRESET
    # ========================================================

    @app_commands.command(
        name="vcreset",
        description="Reinicia las estadísticas de voz de un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés reiniciarle las estadísticas."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def vcreset(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
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

        with conectar() as db:

            db.execute(
                """
                DELETE FROM vc_stats
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    interaction.guild.id,
                    usuario.id
                )
            )

            db.execute(
                """
                DELETE FROM vc_channels
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    interaction.guild.id,
                    usuario.id
                )
            )

            db.execute(
                """
                DELETE FROM vc_daily
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    interaction.guild.id,
                    usuario.id
                )
            )

            db.execute(
                """
                DELETE FROM vc_weekly
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    interaction.guild.id,
                    usuario.id
                )
            )

            db.execute(
                """
                DELETE FROM vc_sessions
                WHERE guild_id = ?
                AND user_id = ?
                """,
                (
                    interaction.guild.id,
                    usuario.id
                )
            )

        # Si sigue en VC, arrancamos una sesión nueva
        if usuario.voice and usuario.voice.channel:

            self.iniciar_sesion(
                usuario,
                usuario.voice.channel
            )

        await interaction.response.send_message(
            f"✅ Reinicié las estadísticas de "
            f"**{usuario.display_name}**.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        VCStats(bot)
    )
```
