import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import time
import asyncio
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "genai.json")
DEFAULT_CONFIG = {
    "enabled": False,
    "random_enabled": True,
    "copy_enabled": True,
    # Probabilidad de responder a un mensaje.
    # 5 = 5%
    "random_chance": 5,
    # Segundos entre respuestas del bot.
    "cooldown": 30,
    # Canal donde puede funcionar.
    # [] = todos los canales.
    "channels": [],
    # Personalidad del bot.
    "personality": (
        "Sos un bot argentino de Discord. "
        "Hablá de manera natural, corta y divertida. "
        "No seas demasiado formal."
    )
}
# ============================================================
# COG
# ============================================================
class GenAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(DATA_FOLDER, exist_ok=True)
        if not os.path.exists(DATA_FILE):
            self.save_data({})
        self.data = self.load_data()
        # Cooldown por servidor
        self.cooldowns = {}
        # Evita responder mensajes enviados muy rápido
        self.processing = set()
        print("[GENAI] Cog cargado.")
    # ========================================================
    # DATA
    # ========================================================
    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
        except Exception as e:
            print(f"[GENAI] Error cargando datos: {e}")
            return {}
    # ========================================================
    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    self.data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )
        except Exception as e:
            print(f"[GENAI] Error guardando datos: {e}")
    # ========================================================
    # CONFIG
    # ========================================================
    def get_config(self, guild_id):
        guild_id = str(guild_id)
        if guild_id not in self.data:
            self.data[guild_id] = DEFAULT_CONFIG.copy()
            self.save_data()
        config = self.data[guild_id]
        # Completar configuraciones antiguas
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        return config
    # ========================================================
    # PANEL
    # ========================================================
    def create_embed(self, guild):
        config = self.get_config(guild.id)
        enabled = config["enabled"]
        random_enabled = config["random_enabled"]
        copy_enabled = config["copy_enabled"]
        status = "🟢 ACTIVADO" if enabled else "🔴 DESACTIVADO"
        random_status = (
            "🟢 Activadas"
            if random_enabled
            else "🔴 Desactivadas"
        )
        copy_status = (
            "🟢 Activada"
            if copy_enabled
            else "🔴 Desactivada"
        )
        channels = config.get("channels", [])
        if channels:
            channel_text = " ".join(
                f"<#{channel_id}>"
                for channel_id in channels
            )
        else:
            channel_text = "Todos los canales"
        embed = discord.Embed(
            title="🤖・GENAI",
            description=(
                "Sistema de respuestas automáticas del servidor.\n\n"
                f"**Estado:** {status}\n\n"
                f"💬 **Respuestas random:** {random_status}\n"
                f"📋 **Copia de mensajes:** {copy_status}\n"
                f"🎲 **Probabilidad:** `{config['random_chance']}%`\n"
                f"⏱️ **Cooldown:** `{config['cooldown']}s`\n"
                f"📍 **Canales:** {channel_text}\n\n"
                "Usá los botones de abajo para configurar el sistema."
            ),
            color=(
                discord.Color.green()
                if enabled
                else discord.Color.red()
            )
        )
        embed.set_footer(
            text="Sistema GenAI"
        )
        return embed
    # ========================================================
    # PANEL VIEW
    # ========================================================
    class GenAIView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog
        # ----------------------------------------------------
        # ACTIVAR / DESACTIVAR
        # ----------------------------------------------------
        @discord.ui.button(
            label="Activar",
            emoji="🟢",
            style=discord.ButtonStyle.success,
            custom_id="genai_enable"
        )
        async def enable(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):
            if interaction.guild is None:
                return
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message(
                    "❌ Solo el dueño del servidor puede configurar GenAI.",
                    ephemeral=True
                )
                return
            config = self.cog.get_config(
                interaction.guild.id
            )
            config["enabled"] = True
            self.cog.save_data()
            await interaction.response.edit_message(
                embed=self.cog.create_embed(
                    interaction.guild
                ),
                view=self
            )
        # ----------------------------------------------------
        # DESACTIVAR
        # ----------------------------------------------------
        @discord.ui.button(
            label="Desactivar",
            emoji="🔴",
            style=discord.ButtonStyle.danger,
            custom_id="genai_disable"
        )
        async def disable(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):
            if interaction.guild is None:
                return
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message(
                    "❌ Solo el dueño del servidor puede configurar GenAI.",
                    ephemeral=True
                )
                return
            config = self.cog.get_config(
                interaction.guild.id
            )
            config["enabled"] = False
            self.cog.save_data()
            await interaction.response.edit_message(
                embed=self.cog.create_embed(
                    interaction.guild
                ),
                view=self
            )
        # ----------------------------------------------------
        # RANDOM
        # ----------------------------------------------------
        @discord.ui.button(
            label="Random",
            emoji="🎲",
            style=discord.ButtonStyle.primary,
            custom_id="genai_random"
        )
        async def random_toggle(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):
            if interaction.guild is None:
                return
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message(
                    "❌ Solo el dueño puede configurar GenAI.",
                    ephemeral=True
                )
                return
            config = self.cog.get_config(
                interaction.guild.id
            )
            config["random_enabled"] = not config["random_enabled"]
            self.cog.save_data()
            await interaction.response.edit_message(
                embed=self.cog.create_embed(
                    interaction.guild
                ),
                view=self
            )
        # ----------------------------------------------------
        # COPIA
        # ----------------------------------------------------
        @discord.ui.button(
            label="Copiar",
            emoji="📋",
            style=discord.ButtonStyle.secondary,
            custom_id="genai_copy"
        )
        async def copy_toggle(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):
            if interaction.guild is None:
                return
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message(
                    "❌ Solo el dueño puede configurar GenAI.",
                    ephemeral=True
                )
                return
            config = self.cog.get_config(
                interaction.guild.id
            )
            config["copy_enabled"] = not config["copy_enabled"]
            self.cog.save_data()
            await interaction.response.edit_message(
                embed=self.cog.create_embed(
                    interaction.guild
                ),
                view=self
            )
        # ----------------------------------------------------
        # CONFIGURACIÓN
        # ----------------------------------------------------
        @discord.ui.button(
            label="Configuración",
            emoji="⚙️",
            style=discord.ButtonStyle.secondary,
            custom_id="genai_config"
        )
        async def config(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):
            if interaction.guild is None:
                return
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message(
                    "❌ Solo el dueño puede configurar GenAI.",
                    ephemeral=True
                )
                return
            await interaction.response.send_message(
                (
                    "⚙️ **Configuración actual**\n\n"
                    "Usá estos comandos:\n\n"
                    "`/genai chance` → Probabilidad de respuesta\n"
                    "`/genai cooldown` → Cooldown\n"
                    "`/genai canal` → Configurar canal\n"
                    "`/genai personalidad` → Cambiar personalidad"
                ),
                ephemeral=True
            )
    # ========================================================
    # /GENAI
    # ========================================================
    genai_group = app_commands.Group(
        name="genai",
        description="Configura el sistema GenAI."
    )
    # ========================================================
    # /GENAI PANEL
    # ========================================================
    @genai_group.command(
        name="panel",
        description="Muestra el panel de configuración de GenAI."
    )
    async def genai_panel(
        self,
        interaction: discord.Interaction
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )
            return
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede usar este panel.",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            embed=self.create_embed(
                interaction.guild
            ),
            view=self.GenAIView(self)
        )
    # ========================================================
    # /GENAI CHANCE
    # ========================================================
    @genai_group.command(
        name="chance",
        description="Configura la probabilidad de respuestas random."
    )
    @app_commands.describe(
        porcentaje="Porcentaje entre 1 y 100."
    )
    async def genai_chance(
        self,
        interaction: discord.Interaction,
        porcentaje: app_commands.Range[int, 1, 100]
    ):
        if interaction.guild is None:
            return
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño puede configurar GenAI.",
                ephemeral=True
            )
            return
        config = self.get_config(
            interaction.guild.id
        )
        config["random_chance"] = porcentaje
        self.save_data()
        await interaction.response.send_message(
            f"🎲 Probabilidad configurada en **{porcentaje}%**.",
            ephemeral=True
        )
    # ========================================================
    # /GENAI COOLDOWN
    # ========================================================
    @genai_group.command(
        name="cooldown",
        description="Configura el cooldown entre respuestas."
    )
    @app_commands.describe(
        segundos="Segundos de cooldown."
    )
    async def genai_cooldown(
        self,
        interaction: discord.Interaction,
        segundos: app_commands.Range[int, 0, 3600]
    ):
        if interaction.guild is None:
            return
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño puede configurar GenAI.",
                ephemeral=True
            )
            return
        config = self.get_config(
            interaction.guild.id
        )
        config["cooldown"] = segundos
        self.save_data()
        await interaction.response.send_message(
            f"⏱️ Cooldown configurado en **{segundos} segundos**.",
            ephemeral=True
        )
    # ========================================================
    # /GENAI CANAL
    # ========================================================
    @genai_group.command(
        name="canal",
        description="Activa o desactiva GenAI en un canal."
    )
    @app_commands.describe(
        canal="Canal donde funcionará GenAI."
    )
    async def genai_canal(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        if interaction.guild is None:
            return
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño puede configurar GenAI.",
                ephemeral=True
            )
            return
        config = self.get_config(
            interaction.guild.id
        )
        channels = config.setdefault(
            "channels",
            []
        )
        if canal.id in channels:
            channels.remove(canal.id)
            texto = (
                f"🔴 GenAI desactivado en {canal.mention}."
            )
        else:
            channels.append(canal.id)
            texto = (
                f"🟢 GenAI activado en {canal.mention}."
            )
        self.save_data()
        await interaction.response.send_message(
            texto,
            ephemeral=True
        )
    # ========================================================
    # /GENAI PERSONALIDAD
    # ========================================================
    @genai_group.command(
        name="personalidad",
        description="Configura la personalidad de GenAI."
    )
    @app_commands.describe(
        texto="Descripción de la personalidad."
    )
    async def genai_personalidad(
        self,
        interaction: discord.Interaction,
        texto: str
    ):
        if interaction.guild is None:
            return
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño puede configurar GenAI.",
                ephemeral=True
            )
            return
        if len(texto) > 1000:
            await interaction.response.send_message(
                "❌ La personalidad no puede superar 1000 caracteres.",
                ephemeral=True
            )
            return
        config = self.get_config(
            interaction.guild.id
        )
        config["personality"] = texto
        self.save_data()
        await interaction.response.send_message(
            "🧠 Personalidad actualizada.",
            ephemeral=True
        )
    # ========================================================
    # /GENAI STATUS
    # ========================================================
    @genai_group.command(
        name="status",
        description="Muestra la configuración actual."
    )
    async def genai_status(
        self,
        interaction: discord.Interaction
    ):
        if interaction.guild is None:
            return
        config = self.get_config(
            interaction.guild.id
        )
        await interaction.response.send_message(
            embed=self.create_embed(
                interaction.guild
            ),
            ephemeral=True
        )
    # ========================================================
    # COMPROBAR CANAL
    # ========================================================
    def channel_allowed(
        self,
        config,
        channel_id
    ):
        channels = config.get(
            "channels",
            []
        )
        # Lista vacía = todos
        if not channels:
            return True
        return channel_id in channels
    # ========================================================
    # COOLDOWN
    # ========================================================
    def on_cooldown(
        self,
        guild_id,
        cooldown
    ):
        now = time.time()
        last = self.cooldowns.get(
            guild_id,
            0
        )
        if now - last < cooldown:
            return True
        self.cooldowns[guild_id] = now
        return False
    # ========================================================
    # COPIA DE MENSAJE
    # ========================================================
    async def copy_message(
        self,
        message
    ):
        content = message.content.strip()
        if not content:
            return False
        # No copiar mensajes demasiado largos
        if len(content) > 300:
            return False
        # Algunas frases que evitamos copiar
        ignored = [
            "http://",
            "https://",
            "discord.gg/",
            "@everyone",
            "@here"
        ]
        if any(
            word in content.lower()
            for word in ignored
        ):
            return False
        # Pequeña probabilidad para que no copie siempre
        if random.randint(1, 100) > 20:
            return False
        try:
            await message.channel.send(
                content,
                allowed_mentions=discord.AllowedMentions.none()
            )
            return True
        except discord.Forbidden:
            return False
        except Exception as e:
            print(
                f"[GENAI] Error copiando mensaje: {e}"
            )
            return False
    # ========================================================
    # RESPUESTAS RANDOM
    # ========================================================
    async def random_response(
        self,
        message
    ):
        # ----------------------------------------------------
        # RESPUESTAS SIMPLES
        # ----------------------------------------------------
        responses = [
            "jajajaj q decís",
            "naaa amigo",
            "💀",
            "JAJAJAJA",
            "literal",
            "real",
            "banco",
            "????",
            "no puede ser",
            "ahre",
            "jsjsjs",
            "qué",
            "me tenté",
            "bro",
            "💀💀💀",
            "facts",
            "mal",
            "re sí",
            "ni en pedo",
            "daleee",
            "a tu jermu",
            "la gordita esa?",
            "te toqué"
        ]
        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------
        response = random.choice(
            responses
        )
        try:
            await message.reply(
                response,
                mention_author=False
            )
        except discord.Forbidden:
            pass
        except Exception as e:
            print(
                f"[GENAI] Error respondiendo: {e}"
            )
    # ========================================================
    # MESSAGE LISTENER
    # ========================================================
    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):
        # ----------------------------------------------------
        # IGNORAR DMS
        # ----------------------------------------------------
        if message.guild is None:
            return
        # ----------------------------------------------------
        # IGNORAR BOTS
        # ----------------------------------------------------
        if message.author.bot:
            return
        # ----------------------------------------------------
        # CONFIG
        # ----------------------------------------------------
        config = self.get_config(
            message.guild.id
        )
        # ----------------------------------------------------
        # SISTEMA APAGADO
        # ----------------------------------------------------
        if not config.get("enabled", False):
            return
        # ----------------------------------------------------
        # CANAL
        # ----------------------------------------------------
        if not self.channel_allowed(
            config,
            message.channel.id
        ):
            return
        # ----------------------------------------------------
        # COOLDOWN
        # ----------------------------------------------------
        cooldown = config.get(
            "cooldown",
            30
        )
        if self.on_cooldown(
            message.guild.id,
            cooldown
        ):
            return
        # ----------------------------------------------------
        # EVITAR PROCESAMIENTO DUPLICADO
        # ----------------------------------------------------
        if message.id in self.processing:
            return
        self.processing.add(
            message.id
        )
        try:
            # =================================================
            # COPIA
            # =================================================
            if config.get(
                "copy_enabled",
                True
            ):
                copied = await self.copy_message(
                    message
                )
                if copied:
                    return
            # =================================================
            # RANDOM
            # =================================================
            if not config.get(
                "random_enabled",
                True
            ):
                return
            chance = config.get(
                "random_chance",
                5
            )
            if random.randint(
                1,
                100
            ) > chance:
                return
            await self.random_response(
                message
            )
        finally:
            self.processing.discard(
                message.id
            )
    # ========================================================
    # ERROR HANDLER
    # ========================================================
    async def cog_app_command_error(
        self,
        interaction,
        error
    ):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    f"❌ Ocurrió un error: `{error}`",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ Ocurrió un error: `{error}`",
                    ephemeral=True
                )
        except Exception:
            pass
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    cog = GenAI(bot)
    await bot.add_cog(cog)

⚠️ Importante

Como este cog usa on_message, en tu bot.py necesitás tener:

intents.message_content = True

Y en Discord Developer Portal también tiene que estar activado Message Content Intent.

Después de poner el archivo en:

cogs/genai.py

reiniciás el bot y usás:

/genai panel

El panel te permite activar/desactivar, prender/apagar respuestas random y copia, y después configurar:

/genai chance 5
/genai cooldown 30
/genai canal #general
/genai personalidad ...

Ojo: la parte llamada random_response() todavía no es una IA generativa real; son respuestas aleatorias predefinidas. Para que sea como GenAI de verdad —que lea el mensaje y genere una respuesta nueva según el contexto— hay que conectarlo a una API de IA.