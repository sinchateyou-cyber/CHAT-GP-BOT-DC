
import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# COG ECO
# ============================================================

class Eco(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print("📢 Eco iniciado.")

    # ========================================================
    # /eco
    # ========================================================

    @app_commands.command(
        name="eco",
        description="Hace que el bot repita un mensaje."
    )
    @app_commands.describe(
        texto="El texto que querés que diga el bot."
    )
    async def eco(
        self,
        interaction: discord.Interaction,
        texto: str
    ):

        # ----------------------------------------------------
        # RESPUESTA PRIVADA
        # ----------------------------------------------------
        # Esto evita que Discord muestre el resultado
        # del comando públicamente.
        await interaction.response.send_message(
            "✅ Mensaje enviado.",
            ephemeral=True
        )

        # ----------------------------------------------------
        # ENVIAR EL TEXTO AL CANAL
        # ----------------------------------------------------

        try:

            await interaction.channel.send(
                texto,
                allowed_mentions=discord.AllowedMentions(
                    everyone=False,
                    users=False,
                    roles=False,
                    replied_user=False
                )
            )

        except discord.Forbidden:

            await interaction.edit_original_response(
                content=(
                    "❌ No tengo permisos para enviar "
                    "mensajes en este canal."
                )
            )

        except Exception as error:

            print(
                f"❌ Error en /eco: "
                f"{type(error).__name__}: {error}"
            )

            await interaction.edit_original_response(
                content="❌ Ocurrió un error al enviar el mensaje."
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Eco(bot)
    )
