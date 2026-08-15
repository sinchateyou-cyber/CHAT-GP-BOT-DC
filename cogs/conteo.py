import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import asyncio


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "counting.json")

DEFAULT_START_NUMBER = 1
ERROR_MESSAGE_DELETE_TIME = 3


# ============================================================
# COG CONTEO
# ============================================================

class Conteo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.save_data({})

        self.data = self.load_data()

        print("[CONTEO] Cog cargado.")

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

            print(
                f"[CONTEO] Error cargando datos: {e}"
            )

            return {}

    # ========================================================

    def save_data(self):

        try:

            os.makedirs(DATA_FOLDER, exist_ok=True)

            with open(DATA_FILE, "w", encoding="utf-8") as f:

                json.dump(
                    self.data,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            print(
                f"[CONTEO] Error guardando datos: {e}"
            )

    # ========================================================
    # CONFIG SERVIDOR
    # ========================================================

    def get_config(self, guild_id):

        guild_id = str(guild_id)

        if guild_id not in self.data:

            self.data[guild_id] = {
                "enabled": False,
                "channel_id": None,
                "current_number": DEFAULT_START_NUMBER
            }

            self.save_data()

        return self.data[guild_id]

    # ========================================================
    # /CONTEO CONFIGURAR
    # ========================================================

    conteo_group = app_commands.Group(
        name="conteo",
        description="Sistema de conteo del servidor."
    )

    @conteo_group.command(
        name="configurar",
        description="Configura el canal de conteo."
    )
    @app_commands.describe(
        canal="Canal donde se realizará el conteo."
    )
    async def configurar(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        # ----------------------------------------------------
        # SOLO OWNER
        # ----------------------------------------------------

        if interaction.user.id != guild.owner_id:

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede configurar el conteo.",
                ephemeral=True
            )

            return

        config = self.get_config(guild.id)

        config["enabled"] = True
        config["channel_id"] = canal.id
        config["current_number"] = DEFAULT_START_NUMBER

        self.save_data()

        embed = discord.Embed(
            title="🔢・CONTEO ACTIVADO",
            description=(
                f"El canal de conteo ahora es {canal.mention}.\n\n"
                "El próximo número es **1**.\n\n"
                "✅ Número correcto → se mantiene.\n"
                "❌ Número incorrecto → se elimina.\n"
                "🤖 El bot avisará cuál era el número correcto.\n\n"
                "El contador continúa aunque alguien se equivoque."
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONTEO DESACTIVAR
    # ========================================================

    @conteo_group.command(
        name="desactivar",
        description="Desactiva el sistema de conteo."
    )
    async def desactivar(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return

        guild = interaction.guild

        if interaction.user.id != guild.owner_id:

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede desactivar el conteo.",
                ephemeral=True
            )

            return

        config = self.get_config(guild.id)

        config["enabled"] = False

        self.save_data()

        await interaction.response.send_message(
            "🔴 **Sistema de conteo desactivado.**",
            ephemeral=True
        )

    # ========================================================
    # /CONTEO ESTADO
    # ========================================================

    @conteo_group.command(
        name="estado",
        description="Muestra el estado actual del conteo."
    )
    async def estado(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return

        config = self.get_config(
            interaction.guild.id
        )

        enabled = config.get(
            "enabled",
            False
        )

        channel_id = config.get(
            "channel_id"
        )

        current_number = config.get(
            "current_number",
            DEFAULT_START_NUMBER
        )

        status = (
            "🟢 Activado"
            if enabled
            else "🔴 Desactivado"
        )

        if channel_id:

            channel = interaction.guild.get_channel(
                channel_id
            )

            channel_text = (
                channel.mention
                if channel
                else f"<#{channel_id}>"
            )

        else:

            channel_text = "No configurado"

        embed = discord.Embed(
            title="🔢・ESTADO DEL CONTEO",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Estado",
            value=status,
            inline=True
        )

        embed.add_field(
            name="Canal",
            value=channel_text,
            inline=True
        )

        embed.add_field(
            name="Próximo número",
            value=f"**{current_number}**",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /CONTEO ESTABLECER
    # ========================================================

    @conteo_group.command(
        name="establecer",
        description="Establece el próximo número del conteo."
    )
    @app_commands.describe(
        numero="Número que deberá escribir el próximo usuario."
    )
    async def establecer(
        self,
        interaction: discord.Interaction,
        numero: app_commands.Range[int, 1, 1000000000]
    ):

        if interaction.guild is None:
            return

        guild = interaction.guild

        if interaction.user.id != guild.owner_id:

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede cambiar el número.",
                ephemeral=True
            )

            return

        config = self.get_config(guild.id)

        config["current_number"] = numero

        self.save_data()

        await interaction.response.send_message(
            f"🔢 El próximo número será **{numero}**.",
            ephemeral=True
        )

    # ========================================================
    # /CONTEO REINICIAR
    # ========================================================

    @conteo_group.command(
        name="reiniciar",
        description="Reinicia el conteo desde 1."
    )
    async def reiniciar(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return

        guild = interaction.guild

        if interaction.user.id != guild.owner_id:

            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede reiniciar el conteo.",
                ephemeral=True
            )

            return

        config = self.get_config(guild.id)

        config["current_number"] = 1

        self.save_data()

        await interaction.response.send_message(
            "🔄 El conteo fue reiniciado.\n\n"
            "El próximo número es **1**.",
            ephemeral=True
        )

    # ========================================================
    # MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        # ----------------------------------------------------
        # IGNORAR BOTS
        # ----------------------------------------------------

        if message.author.bot:
            return

        # ----------------------------------------------------
        # IGNORAR DMS
        # ----------------------------------------------------

        if message.guild is None:
            return

        # ----------------------------------------------------
        # CONFIG
        # ----------------------------------------------------

        config = self.get_config(
            message.guild.id
        )

        # ----------------------------------------------------
        # SISTEMA DESACTIVADO
        # ----------------------------------------------------

        if not config.get(
            "enabled",
            False
        ):
            return

        # ----------------------------------------------------
        # COMPROBAR CANAL
        # ----------------------------------------------------

        channel_id = config.get(
            "channel_id"
        )

        if message.channel.id != channel_id:
            return

        # ----------------------------------------------------
        # OBTENER NÚMERO ESPERADO
        # ----------------------------------------------------

        expected = config.get(
            "current_number",
            DEFAULT_START_NUMBER
        )

        # ----------------------------------------------------
        # LIMPIAR MENSAJE
        # ----------------------------------------------------

        content = message.content.strip()

        # ====================================================
        # COMPROBAR SI ES UN NÚMERO
        # ====================================================

        try:

            number = int(content)

        except (ValueError, TypeError):

            try:
                await message.delete()
            except Exception:
                pass

            try:

                warning = await message.channel.send(
                    f"❌ {message.author.mention}, "
                    f"tenés que poner el número **{expected}**."
                )

                await asyncio.sleep(
                    ERROR_MESSAGE_DELETE_TIME
                )

                await warning.delete()

            except Exception:
                pass

            return

        # ====================================================
        # NÚMERO INCORRECTO
        # ====================================================

        if number != expected:

            # ------------------------------------------------
            # BORRAR EL MENSAJE EQUIVOCADO
            # ------------------------------------------------

            try:

                await message.delete()

            except discord.NotFound:
                pass

            except discord.Forbidden:

                print(
                    "[CONTEO] No tengo permiso para "
                    "borrar mensajes."
                )

            except Exception as e:

                print(
                    f"[CONTEO] Error borrando mensaje: {e}"
                )

            # ------------------------------------------------
            # AVISO
            # ------------------------------------------------

            try:

                warning = await message.channel.send(
                    f"❌ {message.author.mention}, "
                    f"era el número **{expected}**."
                )

                await asyncio.sleep(
                    ERROR_MESSAGE_DELETE_TIME
                )

                await warning.delete()

            except discord.Forbidden:
                pass

            except Exception:
                pass

            # ------------------------------------------------
            # NO CAMBIAR EL CONTADOR
            # ------------------------------------------------

            return

        # ====================================================
        # NÚMERO CORRECTO
        # ====================================================

        config["current_number"] = expected + 1

        self.save_data()

        # El mensaje correcto se queda.
        return


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Conteo(bot)
    )