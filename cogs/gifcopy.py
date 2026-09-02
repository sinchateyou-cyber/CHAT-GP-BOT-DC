import io
import discord
import aiohttp

from discord.ext import commands


class GifCopy(commands.Cog):
    """
    Guarda el último GIF enviado en cada canal.

    Uso:
        /gifcopy

    El comando toma el último GIF detectado en el canal
    y lo vuelve a enviar como archivo GIF.
    """

    def __init__(self, bot):
        self.bot = bot

        # {
        #     channel_id: {
        #         "url": "...",
        #         "message_id": 123456
        #     }
        # }
        self.last_gifs = {}

        self.session = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    # ==========================================================
    # DETECTAR GIFS
    # ==========================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # Ignorar bots
        if message.author.bot:
            return

        # ------------------------------------------------------
        # 1. GIF enviado como archivo
        # ------------------------------------------------------

        for attachment in message.attachments:

            filename = attachment.filename.lower()
            content_type = attachment.content_type or ""

            if (
                filename.endswith(".gif")
                or content_type == "image/gif"
            ):
                self.last_gifs[message.channel.id] = {
                    "url": attachment.url,
                    "message_id": message.id
                }

                return

        # ------------------------------------------------------
        # 2. GIF enviado mediante enlace
        # ------------------------------------------------------

        content = message.content.strip()

        if content:
            urls = content.split()

            for url in urls:

                clean_url = url.split("?")[0].lower()

                if clean_url.endswith(".gif"):
                    self.last_gifs[message.channel.id] = {
                        "url": url,
                        "message_id": message.id
                    }

                    return

    # ==========================================================
    # /gifcopy
    # ==========================================================

    @discord.app_commands.command(
        name="gifcopy",
        description="Copia el último GIF enviado en este canal."
    )
    async def gifcopy(self, interaction: discord.Interaction):

        channel_id = interaction.channel.id

        # ------------------------------------------------------
        # Comprobar si existe un GIF
        # ------------------------------------------------------

        gif_data = self.last_gifs.get(channel_id)

        if not gif_data:
            await interaction.response.send_message(
                "❌ No encontré ningún GIF reciente en este canal.",
                ephemeral=True
            )
            return

        url = gif_data["url"]

        # ------------------------------------------------------
        # Responder inmediatamente para evitar timeout
        # ------------------------------------------------------

        await interaction.response.defer()

        try:

            # --------------------------------------------------
            # Descargar GIF
            # --------------------------------------------------

            async with self.session.get(url) as response:

                if response.status != 200:
                    await interaction.followup.send(
                        "❌ No pude descargar ese GIF.",
                        ephemeral=True
                    )
                    return

                data = await response.read()

            # --------------------------------------------------
            # Comprobar tamaño
            # --------------------------------------------------

            if len(data) > 25 * 1024 * 1024:
                await interaction.followup.send(
                    "❌ Ese GIF es demasiado grande para enviarlo como archivo.",
                    ephemeral=True
                )
                return

            # --------------------------------------------------
            # Crear archivo
            # --------------------------------------------------

            file = discord.File(
                io.BytesIO(data),
                filename="gifcopy.gif"
            )

            # --------------------------------------------------
            # Enviar GIF
            # --------------------------------------------------

            await interaction.followup.send(
                content="🎞️ **GIF copiado**",
                file=file
            )

        except aiohttp.ClientError:
            await interaction.followup.send(
                "❌ No pude acceder al GIF.",
                ephemeral=True
            )

        except Exception as e:
            print(f"[GIFCOPY] Error: {e}")

            await interaction.followup.send(
                "❌ Ocurrió un error al copiar el GIF.",
                ephemeral=True
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(GifCopy(bot))