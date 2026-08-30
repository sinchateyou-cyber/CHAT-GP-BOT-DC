import discord
from discord.ext import commands
from discord import app_commands

import json
import os
import random
import time


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "genai.json")

DEFAULT_CONFIG = {
    "enabled": False,
    "random_enabled": True,
    "copy_enabled": True,
    "random_chance": 5,
    "cooldown": 30,
    "channels": [],
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
            self.data = {}
            self.save_data()
        else:
            self.data = self.load_data()

        self.cooldowns = {}
        self.processing = set()

        print("[GENAI] Cog cargado.")


    # ========================================================
    # DATA
    # ========================================================

    def load_data(self):

        try:
            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):
                    return data

                return {}

        except Exception as error:

            print(
                f"[GENAI] Error cargando datos: {error}"
            )

            return {}


    def save_data(self):

        try:

            os.makedirs(
                DATA_FOLDER,
                exist_ok=True
            )

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

        except Exception as error:

            print(
                f"[GENAI] Error guardando datos: {error}"
            )


    # ========================================================
    # CONFIG
    # ========================================================

    def get_config(self, guild_id):

        guild_id = str(guild_id)

        if guild_id not in self.data:

            self.data[guild_id] = (
                DEFAULT_CONFIG.copy()
            )

            self.data[guild_id]["channels"] = []

            self.save_data()

        config = self.data[guild_id]

        for key, value in DEFAULT_CONFIG.items():

            if key not in config:

                if key == "channels":
                    config[key] = []

                else:
                    config[key] = value

        return config


    # ========================================================
    # EMBED
    # ========================================================

    def create_embed(self, guild):

        config = self.get_config(
            guild.id
        )

        enabled = config.get(
            "enabled",
            False
        )

        random_enabled = config.get(
            "random_enabled",
            True
        )

        copy_enabled = config.get(
            "copy_enabled",
            True
        )

        status = (
            "🟢 ACTIVADO"
            if enabled
            else
            "🔴 DESACTIVADO"
        )

        random_status = (
            "🟢 Activadas"
            if random_enabled
            else
            "🔴 Desactivadas"
        )

        copy_status = (
            "🟢 Activada"
            if copy_enabled
            else
            "🔴 Desactivada"
        )

        channels = config.get(
            "channels",
            []
        )

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
                "Sistema de respuestas automáticas.\n\n"

                f"**Estado:** {status}\n\n"

                f"💬 **Respuestas random:** "
                f"{random_status}\n"

                f"📋 **Copia de mensajes:** "
                f"{copy_status}\n"

                f"🎲 **Probabilidad:** "
                f"`{config.get('random_chance', 5)}%`\n"

                f"⏱️ **Cooldown:** "
                f"`{config.get('cooldown', 30)}s`\n"

                f"📍 **Canales:** "
                f"{channel_text}\n\n"

                "Usá los botones para configurar GenAI."
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
    # VERIFICAR OWNER
    # ========================================================

    def is_owner(
        self,
        interaction
    ):

        return (
            interaction.guild is not None
            and interaction.user.id
            == interaction.guild.owner_id
        )


    # ========================================================
    # PANEL
    # ========================================================

    class GenAIView(discord.ui.View):

        def __init__(self, cog):

            super().__init__(
                timeout=None
            )

            self.cog = cog


        # ----------------------------------------------------
        # ACTIVAR
        # ----------------------------------------------------

        @discord.ui.button(
            label="Activar",
            emoji="🟢",
            style=discord.ButtonStyle.success,
            custom_id="genai_enable"
        )
        async def enable(
            self,
            interaction,
            button
        ):

            if not self.cog.is_owner(
                interaction
            ):

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
            interaction,
            button
        ):

            if not self.cog.is_owner(
                interaction
            ):

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
            interaction,
            button
        ):

            if not self.cog.is_owner(
                interaction
            ):

                await interaction.response.send_message(
                    "❌ Solo el dueño puede configurar GenAI.",
                    ephemeral=True
                )

                return

            config = self.cog.get_config(
                interaction.guild.id
            )

            config["random_enabled"] = not config[
                "random_enabled"
            ]

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
            interaction,
            button
        ):

            if not self.cog.is_owner(
                interaction
            ):

                await interaction.response.send_message(
                    "❌ Solo el dueño puede configurar GenAI.",
                    ephemeral=True
                )

                return

            config = self.cog.get_config(
                interaction.guild.id
            )

            config["copy_enabled"] = not config[
                "copy_enabled"
            ]

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
            interaction,
            button
        ):

            if not self.cog.is_owner(
                interaction
            ):

                await interaction.response.send_message(
                    "❌ Solo el dueño puede configurar GenAI.",
                    ephemeral=True
                )

                return

            await interaction.response.send_message(

                "⚙️ **Configuración de GenAI**\n\n"

                "`/genai chance` → Probabilidad\n"
                "`/genai cooldown` → Cooldown\n"
                "`/genai canal` → Canal\n"
                "`/genai personalidad` → Personalidad\n"
                "`/genai status` → Estado",

                ephemeral=True
            )


    # ========================================================
    # /GENAI PANEL
    # ========================================================

    @app_commands.command(
        name="genai",
        description="Sistema de inteligencia artificial del servidor."
    )
    async def genai(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo funciona en servidores.",
                ephemeral=True
            )

            return

        if not self.is_owner(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede usar GenAI.",
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

    @app_commands.command(
        name="genai-chance",
        description="Configura la probabilidad de GenAI."
    )
    @app_commands.describe(
        porcentaje="Porcentaje entre 1 y 100."
    )
    async def genai_chance(
        self,
        interaction: discord.Interaction,
        porcentaje: app_commands.Range[int, 1, 100]
    ):

        if not self.is_owner(
            interaction
        ):

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

    @app_commands.command(
        name="genai-cooldown",
        description="Configura el cooldown de GenAI."
    )
    @app_commands.describe(
        segundos="Segundos de cooldown."
    )
    async def genai_cooldown(
        self,
        interaction: discord.Interaction,
        segundos: app_commands.Range[int, 0, 3600]
    ):

        if not self.is_owner(
            interaction
        ):

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
            f"⏱️ Cooldown configurado en **{segundos}s**.",
            ephemeral=True
        )


    # ========================================================
    # /GENAI CANAL
    # ========================================================

    @app_commands.command(
        name="genai-canal",
        description="Activa o desactiva GenAI en un canal."
    )
    @app_commands.describe(
        canal="Canal de texto."
    )
    async def genai_canal(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        if not self.is_owner(
            interaction
        ):

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

            channels.remove(
                canal.id
            )

            texto = (
                f"🔴 GenAI desactivado en "
                f"{canal.mention}."
            )

        else:

            channels.append(
                canal.id
            )

            texto = (
                f"🟢 GenAI activado en "
                f"{canal.mention}."
            )

        self.save_data()

        await interaction.response.send_message(
            texto,
            ephemeral=True
        )


    # ========================================================
    # /GENAI PERSONALIDAD
    # ========================================================

    @app_commands.command(
        name="genai-personalidad",
        description="Cambia la personalidad de GenAI."
    )
    @app_commands.describe(
        texto="Nueva personalidad."
    )
    async def genai_personalidad(
        self,
        interaction: discord.Interaction,
        texto: str
    ):

        if not self.is_owner(
            interaction
        ):

            await interaction.response.send_message(
                "❌ Solo el dueño puede configurar GenAI.",
                ephemeral=True
            )

            return

        if len(texto) > 1000:

            await interaction.response.send_message(
                "❌ Máximo 1000 caracteres.",
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

    @app_commands.command(
        name="genai-status",
        description="Muestra el estado de GenAI."
    )
    async def genai_status(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            return

        await interaction.response.send_message(

            embed=self.create_embed(
                interaction.guild
            ),

            ephemeral=True
        )


    # ========================================================
    # CANAL PERMITIDO
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
    # COPIAR MENSAJE
    # ========================================================

    async def copy_message(
        self,
        message
    ):

        content = message.content.strip()

        if not content:
            return False

        if len(content) > 300:
            return False

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

        if random.randint(
            1,
            100
        ) > 20:

            return False

        try:

            await message.channel.send(
                content,
                allowed_mentions=discord.AllowedMentions.none()
            )

            return True

        except Exception:

            return False


    # ========================================================
    # RESPUESTA RANDOM
    # ========================================================

    async def random_response(
        self,
        message
    ):

        responses = [

            "que onda la concha d su madre",
            "si vos no peleas mas q yo gil",
            "toma, aca tenes esta",
            "pareces puta todo el dia pidiendo verga",
            "hola amores",
            "que chota queres?",
            "me amas?",
            "yo te amo🥰",
            "te waskeo toda la carita y q decis?",
            "al de abajo lo cojo todo sin ganas",
            "valen q rico garchas",
            "perdon",
            "este server verga",
            "me agregan y no soy un bot, si existo",
            "mi chele puta",
            "alto moño",
            "arrodillate a chupala",
            "mentira gato, no te enojes ey"
        

        ]

        response = random.choice(
            responses
        )

        try:

            await message.reply(
                response,
                mention_author=False
            )

        except Exception:

            pass


    # ========================================================
    # MESSAGE LISTENER
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        if message.guild is None:
            return

        if message.author.bot:
            return

        config = self.get_config(
            message.guild.id
        )

        if not config.get(
            "enabled",
            False
        ):

            return

        if not self.channel_allowed(
            config,
            message.channel.id
        ):

            return

        if self.on_cooldown(
            message.guild.id,
            config.get(
                "cooldown",
                30
            )
        ):

            return

        if message.id in self.processing:
            return

        self.processing.add(
            message.id
        )

        try:

            if config.get(
                "copy_enabled",
                True
            ):

                copied = await self.copy_message(
                    message
                )

                if copied:
                    return

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


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    cog = GenAI(bot)

    await bot.add_cog(
        cog
    )

    print(
        "✅ [GENAI] Cog registrado."
    )