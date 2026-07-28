import time
from collections import defaultdict, deque
import discord
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN DEL ANTI-SPAM
# ============================================================
# Cantidad de mensajes permitidos
MAX_MESSAGES = 5
# Tiempo en segundos para detectar el spam
TIME_WINDOW = 5
# Cuántos mensajes recientes se eliminan cuando detecta spam
DELETE_MESSAGES = 10
# Tiempo que dura la advertencia antes de borrarse
WARNING_DELETE_AFTER = 8
# Tiempo mínimo entre advertencias al mismo usuario
WARNING_COOLDOWN = 10
# ============================================================
# COG ANTI-SPAM
# ============================================================
class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Guarda los mensajes de cada usuario
        #
        # Formato:
        # guild_id -> user_id -> deque de timestamps
        self.message_history = defaultdict(
            lambda: defaultdict(deque)
        )
        # Guarda los mensajes enviados por el bot
        # para poder eliminarlos posteriormente
        self.recent_messages = defaultdict(
            lambda: defaultdict(deque)
        )
        # Guarda cuándo fue la última advertencia
        self.last_warning = {}
    # ========================================================
    # DETECTAR MENSAJES
    # ========================================================
    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):
        # ----------------------------------------------------
        # IGNORAR MENSAJES DE BOTS
        # ----------------------------------------------------
        if message.author.bot:
            return
        # ----------------------------------------------------
        # IGNORAR MENSAJES PRIVADOS
        # ----------------------------------------------------
        if message.guild is None:
            return
        guild = message.guild
        usuario = message.author
        # ----------------------------------------------------
        # IGNORAR ADMINISTRADORES
        # ----------------------------------------------------
        if usuario.guild_permissions.administrator:
            return
        # ----------------------------------------------------
        # IGNORAR MODERADORES CON GESTIONAR MENSAJES
        # ----------------------------------------------------
        if usuario.guild_permissions.manage_messages:
            return
        # ----------------------------------------------------
        # IDENTIFICADORES
        # ----------------------------------------------------
        guild_id = guild.id
        user_id = usuario.id
        ahora = time.monotonic()
        historial = self.message_history[
            guild_id
        ][user_id]
        # ----------------------------------------------------
        # AGREGAR MENSAJE AL HISTORIAL
        # ----------------------------------------------------
        historial.append(
            ahora
        )
        # ----------------------------------------------------
        # ELIMINAR TIMESTAMPS ANTIGUOS
        # ----------------------------------------------------
        while historial:
            if ahora - historial[0] > TIME_WINDOW:
                historial.popleft()
            else:
                break
        # ----------------------------------------------------
        # COMPROBAR SPAM
        # ----------------------------------------------------
        if len(historial) < MAX_MESSAGES:
            return
        # ----------------------------------------------------
        # EVITAR DETECTAR EL MISMO SPAM REPETIDAMENTE
        # ----------------------------------------------------
        historial.clear()
        # ----------------------------------------------------
        # GUARDAR MENSAJE RECIENTE
        # ----------------------------------------------------
        mensajes_usuario = self.recent_messages[
            guild_id
        ][user_id]
        mensajes_usuario.append(
            message
        )
        # ----------------------------------------------------
        # INTENTAR ELIMINAR MENSAJES RECIENTES
        # ----------------------------------------------------
        try:
            mensajes_a_borrar = list(
                mensajes_usuario
            )
            # Agregar el mensaje actual
            if message not in mensajes_a_borrar:
                mensajes_a_borrar.append(
                    message
                )
            # Eliminar hasta el límite configurado
            mensajes_a_borrar = mensajes_a_borrar[
                -DELETE_MESSAGES:
            ]
            for mensaje in mensajes_a_borrar:
                try:
                    await mensaje.delete()
                except (
                    discord.NotFound,
                    discord.Forbidden,
                    discord.HTTPException
                ):
                    pass
            # Limpiar historial de mensajes
            mensajes_usuario.clear()
        except Exception as error:
            print(
                f"❌ Error eliminando spam: {error}"
            )
        # ----------------------------------------------------
        # CONTROL DE ADVERTENCIAS
        # ----------------------------------------------------
        clave_warning = (
            guild_id,
            user_id
        )
        ultima_advertencia = self.last_warning.get(
            clave_warning,
            0
        )
        # Si todavía está dentro del cooldown,
        # no mandar otra advertencia
        if ahora - ultima_advertencia < WARNING_COOLDOWN:
            return
        self.last_warning[
            clave_warning
        ] = ahora
        # ----------------------------------------------------
        # ENVIAR ADVERTENCIA
        # ----------------------------------------------------
        try:
            advertencia = await message.channel.send(
                f"⚠️ {usuario.mention}, **no hagas spam**. "
                f"El sistema anti-spam detectó demasiados "
                f"mensajes enviados rápidamente."
            )
            # ------------------------------------------------
            # BORRAR ADVERTENCIA DESPUÉS DE UNOS SEGUNDOS
            # ------------------------------------------------
            await advertencia.delete(
                delay=WARNING_DELETE_AFTER
            )
        except discord.Forbidden:
            print(
                "❌ No tengo permisos para enviar "
                "o eliminar mensajes en este canal."
            )
        except discord.HTTPException as error:
            print(
                f"❌ Error enviando advertencia anti-spam: {error}"
            )
    # ========================================================
    # LIMPIAR DATOS CUANDO UN USUARIO SALE
    # ========================================================
    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):
        guild_id = member.guild.id
        user_id = member.id
        # Eliminar historial del usuario
        self.message_history[
            guild_id
        ].pop(
            user_id,
            None
        )
        # Eliminar mensajes guardados
        self.recent_messages[
            guild_id
        ].pop(
            user_id,
            None
        )
        # Eliminar cooldown
        self.last_warning.pop(
            (
                guild_id,
                user_id
            ),
            None
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        AntiSpam(bot)
    )