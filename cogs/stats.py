# cogs/stats.py
# Compatible con discord.py 2.6.3
# Estadísticas estilo Statbot: mensajes + voz

import discord
from discord.ext import commands, tasks
from discord import app_commands

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "stats.json"

# Cada cuánto se guarda el tiempo de voz activo
VOICE_SAVE_INTERVAL = 30


# ============================================================
# UTILIDADES
# ============================================================

def ensure_data_file():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def load_data():
    ensure_data_file()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data):
    ensure_data_file()

    temp_file = DATA_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    temp_file.replace(DATA_FILE)


def format_duration(seconds: int) -> str:
    seconds = max(0, int(seconds))

    days = seconds // 86400
    seconds %= 86400

    hours = seconds // 3600
    seconds %= 3600

    minutes = seconds // 60
    seconds %= 60

    parts = []

    if days:
        parts.append(f"{days}d")

    if hours:
        parts.append(f"{hours}h")

    if minutes:
        parts.append(f"{minutes}m")

    if not parts and seconds:
        parts.append(f"{seconds}s")

    if not parts:
        return "0m"

    return " ".join(parts)


def progress_bar(
    current: int,
    maximum: int,
    length: int = 10
) -> str:

    if maximum <= 0:
        return "⬜" * length

    percentage = min(current / maximum, 1)

    filled = int(length * percentage)

    return "🟪" * filled + "⬜" * (length - filled)


def get_today_key():
    return datetime.now().strftime("%Y-%m-%d")


def get_week_key():
    now = datetime.now()
    return f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"


def get_month_key():
    return datetime.now().strftime("%Y-%m")


# ============================================================
# COG
# ============================================================

class Stats(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Sesiones de voz activas
        #
        # (guild_id, user_id):
        # {
        #     "started": timestamp,
        #     "channel_id": channel_id
        # }
        self.voice_sessions = {}

        self.save_voice_loop.start()

    def cog_unload(self):
        self.save_voice_loop.cancel()

        # Guardar datos pendientes
        try:
            self.flush_all_voice_sessions()
        except Exception:
            pass

    # ========================================================
    # ESTRUCTURA DE DATOS
    # ========================================================

    def get_user_data(self, guild_id: int, user_id: int):

        data = load_data()

        guild_key = str(guild_id)
        user_key = str(user_id)

        if guild_key not in data:
            data[guild_key] = {
                "users": {}
            }

        guild_data = data[guild_key]

        if "users" not in guild_data:
            guild_data["users"] = {}

        if user_key not in guild_data["users"]:
            guild_data["users"][user_key] = {
                "messages": {
                    "total": 0,
                    "daily": {},
                    "weekly": {},
                    "monthly": {}
                },

                "voice": {
                    "total": 0,
                    "daily": {},
                    "weekly": {},
                    "monthly": {},
                    "channels": {}
                }
            }

        user = guild_data["users"][user_key]

        # Compatibilidad por si falta alguna parte
        user.setdefault("messages", {})
        user["messages"].setdefault("total", 0)
        user["messages"].setdefault("daily", {})
        user["messages"].setdefault("weekly", {})
        user["messages"].setdefault("monthly", {})

        user.setdefault("voice", {})
        user["voice"].setdefault("total", 0)
        user["voice"].setdefault("daily", {})
        user["voice"].setdefault("weekly", {})
        user["voice"].setdefault("monthly", {})
        user["voice"].setdefault("channels", {})

        return data, user

    # ========================================================
    # MENSAJES
    # ========================================================

    def register_message(self, message: discord.Message):

        data, user = self.get_user_data(
            message.guild.id,
            message.author.id
        )

        today = get_today_key()
        week = get_week_key()
        month = get_month_key()

        messages = user["messages"]

        messages["total"] += 1

        messages["daily"][today] = (
            messages["daily"].get(today, 0) + 1
        )

        messages["weekly"][week] = (
            messages["weekly"].get(week, 0) + 1
        )

        messages["monthly"][month] = (
            messages["monthly"].get(month, 0) + 1
        )

        save_data(data)

    @commands.Cog.listener()
    async def on_message(self, message):

        # Ignorar DMs
        if message.guild is None:
            return

        # Ignorar bots
        if message.author.bot:
            return

        try:
            self.register_message(message)
        except Exception as e:
            print(f"[STATS] Error registrando mensaje: {e}")

    # ========================================================
    # VOZ
    # ========================================================

    def add_voice_seconds(
        self,
        member: discord.Member,
        seconds: int,
        channel_id: Optional[int] = None
    ):

        if seconds <= 0:
            return

        data, user = self.get_user_data(
            member.guild.id,
            member.id
        )

        seconds = int(seconds)

        today = get_today_key()
        week = get_week_key()
        month = get_month_key()

        voice = user["voice"]

        voice["total"] += seconds

        voice["daily"][today] = (
            voice["daily"].get(today, 0) + seconds
        )

        voice["weekly"][week] = (
            voice["weekly"].get(week, 0) + seconds
        )

        voice["monthly"][month] = (
            voice["monthly"].get(month, 0) + seconds
        )

        if channel_id is not None:

            channel_key = str(channel_id)

            voice["channels"][channel_key] = (
                voice["channels"].get(channel_key, 0)
                + seconds
            )

        save_data(data)

    # ========================================================
    # ENTRADA / SALIDA DE VOZ
    # ========================================================

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):

        if member.bot:
            return

        key = (
            member.guild.id,
            member.id
        )

        # ----------------------------------------------------
        # ENTRÓ A VOZ
        # ----------------------------------------------------

        if before.channel is None and after.channel is not None:

            # No contar AFK
            if member.guild.afk_channel:
                if after.channel.id == member.guild.afk_channel.id:
                    return

            self.voice_sessions[key] = {
                "started": time.time(),
                "channel_id": after.channel.id
            }

            return

        # ----------------------------------------------------
        # SALIÓ DE VOZ
        # ----------------------------------------------------

        if before.channel is not None and after.channel is None:

            session = self.voice_sessions.pop(key, None)

            if session is None:
                return

            elapsed = int(
                time.time() - session["started"]
            )

            self.add_voice_seconds(
                member,
                elapsed,
                session["channel_id"]
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

            session = self.voice_sessions.pop(key, None)

            if session:

                elapsed = int(
                    time.time() - session["started"]
                )

                self.add_voice_seconds(
                    member,
                    elapsed,
                    session["channel_id"]
                )

            # Si entró al AFK, dejamos de contar
            if member.guild.afk_channel:

                if after.channel.id == member.guild.afk_channel.id:
                    return

            self.voice_sessions[key] = {
                "started": time.time(),
                "channel_id": after.channel.id
            }

    # ========================================================
    # GUARDADO PERIÓDICO DE VOZ
    # ========================================================

    @tasks.loop(seconds=VOICE_SAVE_INTERVAL)
    async def save_voice_loop(self):

        now = time.time()

        for key, session in list(
            self.voice_sessions.items()
        ):

            guild_id, user_id = key

            guild = self.bot.get_guild(guild_id)

            if guild is None:
                continue

            member = guild.get_member(user_id)

            if member is None:
                self.voice_sessions.pop(key, None)
                continue

            # Si ya no está en voz
            if member.voice is None:
                self.voice_sessions.pop(key, None)
                continue

            if member.voice.channel is None:
                self.voice_sessions.pop(key, None)
                continue

            # AFK no cuenta
            if guild.afk_channel:

                if member.voice.channel.id == guild.afk_channel.id:
                    self.voice_sessions.pop(key, None)
                    continue

            elapsed = int(
                now - session["started"]
            )

            if elapsed <= 0:
                continue

            self.add_voice_seconds(
                member,
                elapsed,
                session["channel_id"]
            )

            # Reiniciar contador de sesión
            self.voice_sessions[key] = {
                "started": now,
                "channel_id": session["channel_id"]
            }

    @save_voice_loop.before_loop
    async def before_save_voice_loop(self):

        await self.bot.wait_until_ready()

    # ========================================================
    # FLUSH AL DESCARGAR
    # ========================================================

    def flush_all_voice_sessions(self):

        now = time.time()

        for key, session in list(
            self.voice_sessions.items()
        ):

            guild_id, user_id = key

            guild = self.bot.get_guild(guild_id)

            if guild is None:
                continue

            member = guild.get_member(user_id)

            if member is None:
                continue

            elapsed = int(
                now - session["started"]
            )

            if elapsed <= 0:
                continue

            self.add_voice_seconds(
                member,
                elapsed,
                session["channel_id"]
            )

            self.voice_sessions[key] = {
                "started": now,
                "channel_id": session["channel_id"]
            }

    # ========================================================
    # ESTADÍSTICAS
    # ========================================================

    def get_stats(
        self,
        guild: discord.Guild,
        member: discord.Member
    ):

        data, user = self.get_user_data(
            guild.id,
            member.id
        )

        messages = user["messages"]
        voice = user["voice"]

        today = get_today_key()
        week = get_week_key()
        month = get_month_key()

        total_messages = messages["total"]
        today_messages = messages["daily"].get(today, 0)
        week_messages = messages["weekly"].get(week, 0)
        month_messages = messages["monthly"].get(month, 0)

        total_voice = voice["total"]
        today_voice = voice["daily"].get(today, 0)
        week_voice = voice["weekly"].get(week, 0)
        month_voice = voice["monthly"].get(month, 0)

        # Agregar tiempo de sesión actual
        key = (
            guild.id,
            member.id
        )

        if key in self.voice_sessions:

            session = self.voice_sessions[key]

            current = int(
                time.time() - session["started"]
            )

            total_voice += current

            # El tiempo actual pertenece al día actual
            today_voice += current
            week_voice += current
            month_voice += current

        return {
            "messages_total": total_messages,
            "messages_today": today_messages,
            "messages_week": week_messages,
            "messages_month": month_messages,

            "voice_total": total_voice,
            "voice_today": today_voice,
            "voice_week": week_voice,
            "voice_month": month_voice
        }

    # ========================================================
    # RANKING MENSAJES
    # ========================================================

    def message_ranking(self, guild):

        data = load_data()

        guild_data = data.get(
            str(guild.id),
            {}
        )

        users = guild_data.get(
            "users",
            {}
        )

        ranking = []

        for user_id, user_data in users.items():

            member = guild.get_member(
                int(user_id)
            )

            if member is None:
                continue

            amount = int(
                user_data
                .get("messages", {})
                .get("total", 0)
            )

            ranking.append(
                (member, amount)
            )

        ranking.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return ranking

    # ========================================================
    # RANKING VOZ
    # ========================================================

    def voice_ranking(self, guild):

        data = load_data()

        guild_data = data.get(
            str(guild.id),
            {}
        )

        users = guild_data.get(
            "users",
            {}
        )

        ranking = []

        now = time.time()

        for user_id, user_data in users.items():

            member = guild.get_member(
                int(user_id)
            )

            if member is None:
                continue

            amount = int(
                user_data
                .get("voice", {})
                .get("total", 0)
            )

            key = (
                guild.id,
                member.id
            )

            if key in self.voice_sessions:

                amount += int(
                    now
                    - self.voice_sessions[key]["started"]
                )

            ranking.append(
                (member, amount)
            )

        ranking.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return ranking

    # ========================================================
    # BUSCAR POSICIÓN
    # ========================================================

    def get_message_position(
        self,
        guild,
        member
    ):

        ranking = self.message_ranking(guild)

        for position, (user, amount) in enumerate(
            ranking,
            start=1
        ):

            if user.id == member.id:
                return position

        return None

    def get_voice_position(
        self,
        guild,
        member
    ):

        ranking = self.voice_ranking(guild)

        for position, (user, amount) in enumerate(
            ranking,
            start=1
        ):

            if user.id == member.id:
                return position

        return None

    # ========================================================
    # /STATS
    # ========================================================

    @commands.hybrid_command(
        name="stats",
        description="Muestra tus estadísticas del servidor."
    )
    @app_commands.describe(
        usuario="Usuario del que querés ver las estadísticas."
    )
    async def stats(
        self,
        ctx: commands.Context,
        usuario: Optional[discord.Member] = None
    ):

        if ctx.guild is None:
            await ctx.send(
                "❌ Este comando solamente funciona dentro de un servidor."
            )
            return

        member = usuario or ctx.author

        data = self.get_stats(
            ctx.guild,
            member
        )

        message_position = self.get_message_position(
            ctx.guild,
            member
        )

        voice_position = self.get_voice_position(
            ctx.guild,
            member
        )

        embed = discord.Embed(
            title=f"📊 Estadísticas de {member.display_name}",
            description=(
                f"**Servidor:** {ctx.guild.name}\n"
                f"**Usuario:** {member.mention}"
            ),
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        # ----------------------------------------------------
        # MENSAJES
        # ----------------------------------------------------

        embed.add_field(
            name="💬 Mensajes",
            value=(
                f"**Total:** `{data['messages_total']:,}`\n"
                f"**Hoy:** `{data['messages_today']:,}`\n"
                f"**Esta semana:** `{data['messages_week']:,}`\n"
                f"**Este mes:** `{data['messages_month']:,}`\n"
                f"**Ranking:** `#{message_position or '-'}"
            ),
            inline=True
        )

        # ----------------------------------------------------
        # VOZ
        # ----------------------------------------------------

        embed.add_field(
            name="🎤 Actividad de voz",
            value=(
                f"**Total:** `{format_duration(data['voice_total'])}`\n"
                f"**Hoy:** `{format_duration(data['voice_today'])}`\n"
                f"**Esta semana:** `{format_duration(data['voice_week'])}`\n"
                f"**Este mes:** `{format_duration(data['voice_month'])}`\n"
                f"**Ranking:** `#{voice_position or '-'}"
            ),
            inline=True
        )

        # ----------------------------------------------------
        # RESUMEN
        # ----------------------------------------------------

        embed.add_field(
            name="📈 Resumen",
            value=(
                f"💬 **{data['messages_total']:,}** mensajes enviados\n"
                f"🎤 **{format_duration(data['voice_total'])}** en voz"
            ),
            inline=False
        )

        embed.set_footer(
            text="Server Stats • Mensajes + Voz"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # /STATS RANK
    # ========================================================

    @commands.hybrid_command(
        name="statsrank",
        description="Muestra el ranking de actividad del servidor."
    )
    @app_commands.describe(
        categoria="Categoría del ranking."
    )
    @app_commands.choices(
        categoria=[
            app_commands.Choice(
                name="💬 Mensajes",
                value="mensajes"
            ),
            app_commands.Choice(
                name="🎤 Voz",
                value="voz"
            )
        ]
    )
    async def statsrank(
        self,
        ctx: commands.Context,
        categoria: str = "mensajes"
    ):

        if ctx.guild is None:
            await ctx.send(
                "❌ Este comando solamente funciona dentro de un servidor."
            )
            return

        if categoria.lower() in (
            "voz",
            "voice",
            "v"
        ):

            ranking = self.voice_ranking(
                ctx.guild
            )

            title = "🎤 Ranking de Voz"

        else:

            ranking = self.message_ranking(
                ctx.guild
            )

            title = "💬 Ranking de Mensajes"

        if not ranking:

            await ctx.send(
                "📊 Todavía no hay estadísticas registradas."
            )
            return

        description = []

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }

        for position, (member, amount) in enumerate(
            ranking[:10],
            start=1
        ):

            medal = medals.get(
                position,
                f"`#{position}`"
            )

            if categoria.lower() in (
                "voz",
                "voice",
                "v"
            ):

                value = format_duration(amount)

            else:

                value = f"{amount:,} mensajes"

            description.append(
                f"{medal} **{member.display_name}** — `{value}`"
            )

        embed = discord.Embed(
            title=title,
            description="\n".join(description),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=f"{ctx.guild.name} • Top 10"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # /VOICERANK
    # ========================================================

    @commands.hybrid_command(
        name="voicerank",
        description="Muestra el ranking de tiempo en voz."
    )
    async def voicerank(
        self,
        ctx: commands.Context
    ):

        if ctx.guild is None:
            await ctx.send(
                "❌ Este comando solamente funciona dentro de un servidor."
            )
            return

        ranking = self.voice_ranking(
            ctx.guild
        )

        if not ranking:

            await ctx.send(
                "🎤 Todavía no hay actividad de voz registrada."
            )
            return

        lines = []

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }

        for position, (member, seconds) in enumerate(
            ranking[:10],
            start=1
        ):

            medal = medals.get(
                position,
                f"`#{position}`"
            )

            lines.append(
                f"{medal} **{member.display_name}** — "
                f"`{format_duration(seconds)}`"
            )

        embed = discord.Embed(
            title="🎤 Ranking de Voz",
            description="\n".join(lines),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=f"{ctx.guild.name} • Top 10"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # /MSGRANK
    # ========================================================

    @commands.hybrid_command(
        name="msgrank",
        description="Muestra el ranking de mensajes enviados."
    )
    async def msgrank(
        self,
        ctx: commands.Context
    ):

        if ctx.guild is None:
            await ctx.send(
                "❌ Este comando solamente funciona dentro de un servidor."
            )
            return

        ranking = self.message_ranking(
            ctx.guild
        )

        if not ranking:

            await ctx.send(
                "💬 Todavía no hay mensajes registrados."
            )
            return

        lines = []

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }

        for position, (member, amount) in enumerate(
            ranking[:10],
            start=1
        ):

            medal = medals.get(
                position,
                f"`#{position}`"
            )

            lines.append(
                f"{medal} **{member.display_name}** — "
                f"`{amount:,} mensajes`"
            )

        embed = discord.Embed(
            title="💬 Ranking de Mensajes",
            description="\n".join(lines),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=f"{ctx.guild.name} • Top 10"
        )

        await ctx.send(embed=embed)

    # ========================================================
    # /ACTIVITY
    # ========================================================

    @commands.hybrid_command(
        name="activity",
        description="Muestra un resumen de tu actividad."
    )
    async def activity(
        self,
        ctx: commands.Context
    ):

        if ctx.guild is None:
            await ctx.send(
                "❌ Este comando solamente funciona dentro de un servidor."
            )
            return

        member = ctx.author

        stats = self.get_stats(
            ctx.guild,
            member
        )

        embed = discord.Embed(
            title=f"📈 Actividad de {member.display_name}",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="💬 Mensajes",
            value=(
                f"Hoy: `{stats['messages_today']:,}`\n"
                f"Semana: `{stats['messages_week']:,}`\n"
                f"Total: `{stats['messages_total']:,}`"
            ),
            inline=True
        )

        embed.add_field(
            name="🎤 Voz",
            value=(
                f"Hoy: `{format_duration(stats['voice_today'])}`\n"
                f"Semana: `{format_duration(stats['voice_week'])}`\n"
                f"Total: `{format_duration(stats['voice_total'])}`"
            ),
            inline=True
        )

        await ctx.send(embed=embed)

    # ========================================================
    # /RESETSTATS
    # ========================================================

    @commands.hybrid_command(
        name="resetstats",
        description="Reinicia las estadísticas de un usuario."
    )
    @commands.has_guild_permissions(
        administrator=True
    )
    @app_commands.describe(
        usuario="Usuario al que querés reiniciar las estadísticas."
    )
    async def resetstats(
        self,
        ctx: commands.Context,
        usuario: discord.Member
    ):

        if ctx.guild is None:
            return

        data = load_data()

        guild_key = str(ctx.guild.id)
        user_key = str(usuario.id)

        if guild_key in data:

            users = data[guild_key].get(
                "users",
                {}
            )

            if user_key in users:
                del users[user_key]

        # Reiniciar sesión activa si existe
        self.voice_sessions.pop(
            (
                ctx.guild.id,
                usuario.id
            ),
            None
        )

        save_data(data)

        await ctx.send(
            f"✅ Se reiniciaron las estadísticas de "
            f"**{usuario.display_name}**."
        )

    # ========================================================
    # ERROR DEL RESET
    # ========================================================

    @resetstats.error
    async def resetstats_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás permisos de **Administrador** "
                "para usar este comando."
            )

        elif isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            await ctx.send(
                "❌ Tenés que indicar un usuario.\n"
                "Ejemplo: `sresetstats @usuario`"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Stats(bot)
    )