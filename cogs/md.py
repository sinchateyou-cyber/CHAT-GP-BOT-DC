# cogs/md.py

import discord
from discord.ext import commands
from discord import app_commands


class MD(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /md
    # ========================================================

    @app_commands.command(
        name="md",
        description="Envía un mensaje privado a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés enviarle el DM.",
        mensaje="Mensaje que querés enviar."
    )
    @app_commands.default_permissions(administrator=True)
    async def md(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        mensaje: str
    ):

        # ----------------------------------------------------
        # SEGURIDAD
        # ----------------------------------------------------

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ No tenés permisos para usar este comando.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # EVITAR DM AL BOT
        # ----------------------------------------------------

        if usuario.bot:

            return await interaction.response.send_message(
                "❌ No podés enviarle un DM a un bot.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # RESPUESTA INICIAL
        # ----------------------------------------------------

        await interaction.response.defer(
            ephemeral=True
        )

        # ----------------------------------------------------
        # EMBED DEL DM
        # ----------------------------------------------------

        embed = discord.Embed(
            title="💌 Nuevo mensaje",
            description=mensaje,
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text=interaction.guild.name
        )

        # ----------------------------------------------------
        # ENVIAR DM
        # ----------------------------------------------------

        try:

            await usuario.send(
                embed=embed
            )

        except discord.Forbidden:

            return await interaction.followup.send(
                f"❌ No pude enviarle un DM a "
                f"**{usuario.display_name}**.\n\n"
                "Puede tener los mensajes privados cerrados.",
                ephemeral=True
            )

        except discord.HTTPException:

            return await interaction.followup.send(
                "❌ Discord rechazó el mensaje privado.",
                ephemeral=True
            )

        except Exception as error:

            print(
                f"❌ Error enviando DM: {error}"
            )

            return await interaction.followup.send(
                "❌ Ocurrió un error enviando el DM.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # CONFIRMACIÓN
        # ----------------------------------------------------

        await interaction.followup.send(
            f"✅ DM enviado correctamente a "
            f"**{usuario.display_name}**.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        MD(bot)
    )