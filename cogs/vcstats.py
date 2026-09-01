import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "vc_stats.json"


# ============================================================
# DATOS
# ============================================================

def cargar_datos():

    DATA_FOLDER.mkdir(exist_ok=True)

    if not DATA_FILE.exists():

        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )

    try:

        return json.loads(
            DATA_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return {}


def guardar_datos(data):

    DATA_FOLDER.mkdir(exist_ok=True)

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# TIEMPO
# ============================================================

def ahora():

    return datetime.now(
        timezone.utc
    )


def timestamp():

    return ahora().timestamp()


def formatear_tiempo(segundos):

    segundos = int(max(0, segundos))

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
# ESTRUCTURA DE USUARIO
# ============================================================

def obtener_usuario(data, guild_id, user_id):

    guild_id = str(guild_id)
    user_id = str(user_id)

    if guild_id not in data:

        data[guild_id] = {}

    if user_id not in data[guild_id]:

        data[guild_id][user_id] = {

            "total_seconds": 0,

            "sessions": 0,

            "channels": {},

            "daily": {},

            "weekly": {},

            "current_session": None
        }

    return data[guild_id][user_id]


# ============================================================
# COG
# ============================================================

class VCStats(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = cargar_datos()

        print(
            "🎙️ VCStats iniciado."
        )

    # ========================================================
    # ENTRAR / SALIR DE VC
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
        # ENTRÓ A VC
        # ----------------------------------------------------

        if before.channel is None and after.channel is not None:

            await self.iniciar_sesion(
                member,
                after.channel
            )

            return

        # ----------------------------------------------------
        # SALIÓ DE VC
        # ----------------------------------------------------

        if before.channel is not None and after.channel is None:

            await self.finalizar_sesion(
                member
            )

            return

        # ----------------------------------------------------
        # CAMBIÓ DE VC
        # ----------------------------------------------------

        if (
            before.channel is not None
            and after.channel is not None
            and before.channel.id != after.channel.id
        ):

            await self.cambiar_canal(
                member,
                after.channel
            )

    # ========================================================
    # INICIAR SESIÓN
    # ========================================================

    async def iniciar_sesion(
        self,
        member,
        channel
    ):

        usuario = obtener_usuario(
            self.data,
            member.guild.id,
            member.id
        )

        usuario["current_session"] = {

            "started_at":
                timestamp(),

            "channel_id":
                channel.id,

            "channel_name":
                channel.name
        }

        guardar_datos(
            self.data
        )

        print(
            f"🎙️ {member} entró a "
            f"{channel.name}"
        )

    # ========================================================
    # FINALIZAR SESIÓN
    # ========================================================

    async def finalizar_sesion(
        self,
        member
    ):

        usuario = obtener_usuario(
            self.data,
            member.guild.id,
            member.id
        )

        sesion = usuario.get(
            "current_session"
        )

        if not sesion:

            return

        inicio = sesion.get(
            "started_at",
            timestamp()
        )

        fin = timestamp()

        duracion = max(
            0,
            fin - inicio
        )

        canal_id = str(
            sesion.get(
                "channel_id"
            )
        )

        canal_nombre = sesion.get(
            "channel_name",
            "Canal desconocido"
        )

        # ----------------------------------------------------
        # TOTAL
        # ----------------------------------------------------

        usuario["total_seconds"] += duracion

        # ----------------------------------------------------
        # SESIONES
        # ----------------------------------------------------

        usuario["sessions"] += 1

        # ----------------------------------------------------
        # CANALES
        # ----------------------------------------------------

        if canal_id not in usuario["channels"]:

            usuario["channels"][canal_id] = {

                "name":
                    canal_nombre,

                "seconds":
                    0
            }

        usuario["channels"][canal_id][
            "seconds"
        ] += duracion

        # ----------------------------------------------------
        # DÍA
        # ----------------------------------------------------

        fecha = datetime.fromtimestamp(
            fin,
            timezone.utc
        ).strftime(
            "%Y-%m-%d"
        )

        if fecha not in usuario["daily"]:

            usuario["daily"][fecha] = 0

        usuario["daily"][fecha] += duracion

        # ----------------------------------------------------
        # SEMANA
        # ----------------------------------------------------

        dt = datetime.fromtimestamp(
            fin,
            timezone.utc
        )

        year, week, _ = dt.isocalendar()

        semana = f"{year}-W{week:02d}"

        if semana not in usuario["weekly"]:

            usuario["weekly"][semana] = 0

        usuario["weekly"][semana] += duracion

        # ----------------------------------------------------
        # BORRAR SESIÓN ACTUAL
        # ----------------------------------------------------

        usuario["current_session"] = None

        guardar_datos(
            self.data
        )

        print(
            f"🎙️ {member} salió de VC "
            f"({formatear_tiempo(duracion)})"
        )

    # ========================================================
    # CAMBIAR DE CANAL
    # ========================================================

    async def cambiar_canal(
        self,
        member,
        nuevo_canal
    ):

        await self.finalizar_sesion(
            member
        )

        await self.iniciar_sesion(
            member,
            nuevo_canal
        )

    # ========================================================
    # CALCULAR SESIÓN ACTUAL
    # ========================================================

    def obtener_total_actual(
        self,
        usuario
    ):

        total = usuario.get(
            "total_seconds",
            0
        )

        sesion = usuario.get(
            "current_session"
        )

        if sesion:

            inicio = sesion.get(
                "started_at"
            )

            if inicio:

                total += max(
                    0,
                    timestamp() - inicio
                )

        return total

    # ========================================================
    # TIEMPO DE HOY
    # ========================================================

    def obtener_hoy(
        self,
        usuario
    ):

        fecha = ahora().strftime(
            "%Y-%m-%d"
        )

        total = usuario.get(
            "daily",
            {}
        ).get(
            fecha,
            0
        )

        sesion = usuario.get(
            "current_session"
        )

        if sesion:

            inicio = sesion.get(
                "started_at"
            )

            if inicio:

                inicio_dt = datetime.fromtimestamp(
                    inicio,
                    timezone.utc
                )

                if inicio_dt.strftime(
                    "%Y-%m-%d"
                ) == fecha:

                    total += max(
                        0,
                        timestamp() - inicio
                    )

        return total

    # ========================================================
    # TIEMPO DE ESTA SEMANA
    # ========================================================

    def obtener_semana(
        self,
        usuario
    ):

        dt = ahora()

        year, week, _ = dt.isocalendar()

        semana = f"{year}-W{week:02d}"

        total = usuario.get(
            "weekly",
            {}
        ).get(
            semana,
            0
        )

        sesion = usuario.get(
            "current_session"
        )

        if sesion:

            inicio = sesion.get(
                "started_at"
            )

            if inicio:

                total += max(
                    0,
                    timestamp() - inicio
                )

        return total

    # ========================================================
    # CANAL MÁS USADO
    # ========================================================

    def obtener_canal_top(
        self,
        usuario
    ):

        canales = usuario.get(
            "channels",
            {}
        )

        if not canales:

            return None

        canal_id, datos = max(
            canales.items(),
            key=lambda item:
                item[1].get(
                    "seconds",
                    0
                )
        )

        return datos

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

        datos = obtener_usuario(
            self.data,
            interaction.guild.id,
            usuario.id
        )

        total = self.obtener_total_actual(
            datos
        )

        hoy = self.obtener_hoy(
            datos
        )

        semana = self.obtener_semana(
            datos
        )

        sesiones = datos.get(
            "sessions",
            0
        )

        canal_top = self.obtener_canal_top(
            datos
        )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title=f"🎙️ Estadísticas de voz",
            description=(
                f"### {usuario.display_name}\n\n"
                f"⏱️ **Tiempo total:** "
                f"{formatear_tiempo(total)}\n\n"
                f"📅 **Hoy:** "
                f"{formatear_tiempo(hoy)}\n\n"
                f"📆 **Esta semana:** "
                f"{formatear_tiempo(semana)}\n\n"
                f"🎧 **Sesiones:** "
                f"{sesiones}"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        if canal_top:

            embed.add_field(
                name="🏆 Canal más usado",
                value=(
                    f"**{canal_top.get('name', 'Desconocido')}**\n"
                    f"⏱️ {formatear_tiempo(canal_top.get('seconds', 0))}"
                ),
                inline=False
            )

        if datos.get(
            "current_session"
        ):

            canal_actual = datos[
                "current_session"
            ].get(
                "channel_name",
                "Desconocido"
            )

            embed.add_field(
                name="🟢 Actualmente",
                value=(
                    f"Está en **{canal_actual}**"
                ),
                inline=False
            )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=f"{interaction.guild.name}"
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

        guild_id = str(
            interaction.guild.id
        )

        user_id = str(
            usuario.id
        )

        if guild_id not in self.data:

            self.data[guild_id] = {}

        self.data[guild_id][user_id] = {

            "total_seconds": 0,

            "sessions": 0,

            "channels": {},

            "daily": {},

            "weekly": {},

            "current_session": None
        }

        # ----------------------------------------------------
        # SI ESTÁ EN VC, EMPEZAR NUEVA SESIÓN
        # ----------------------------------------------------

        if usuario.voice and usuario.voice.channel:

            self.data[guild_id][user_id][
                "current_session"
            ] = {

                "started_at":
                    timestamp(),

                "channel_id":
                    usuario.voice.channel.id,

                "channel_name":
                    usuario.voice.channel.name
            }

        guardar_datos(
            self.data
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
