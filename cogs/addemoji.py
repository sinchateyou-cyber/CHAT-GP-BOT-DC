import discord
from discord import app_commands
from discord.ext import commands


class AddEmoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="addemoji",
        description="Agrega un emoji al servidor."
    )
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def addemoji(
        self,
        interaction: discord.Interaction,
        nombre: str,
        imagen: discord.Attachment
    ):
        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            return await interaction.response.send_message(
                "❌ El archivo debe ser una imagen.",
                ephemeral=True
            )

        try:
            datos = await imagen.read()

            emoji = await interaction.guild.create_custom_emoji(
                name=nombre,
                image=datos
            )

            await interaction.response.send_message(
                f"✅ Emoji agregado correctamente: {emoji} `{nombre}`"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para administrar emojis.",
                ephemeral=True
            )

        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ No se pudo agregar el emoji. Puede que hayas alcanzado el límite de emojis.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(AddEmoji(bot))