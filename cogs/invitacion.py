import discord
from discord.ext import commands
from discord import app_commands


class Invitacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /invitacion
    # ========================================================

    @app_commands.command(
        name="invitacion",
        description="Crea una invitación para este servidor."
    )
    @app_commands.default_permissions(administrator=True)
    async def invitacion(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message(
                "❌ No tenés permisos para usar este comando.",
                ephemeral=True
            )

        await interaction.response.defer()

        # ====================================================
        # BUSCAR UN CANAL DONDE SE PUEDA CREAR INVITACIÓN
        # ====================================================

        canal = None

        # Primero intenta encontrar un canal de texto
        # donde el bot pueda crear invitaciones.
        for channel in interaction.guild.text_channels:

            permissions = channel.permissions_for(
                interaction.guild.me
            )

            if permissions.create_instant_invite:
                canal = channel
                break

        if canal is None:

            return await interaction.followup.send(
                "❌ No encontré ningún canal donde pueda "
                "crear invitaciones."
            )

        # ====================================================
        # CREAR INVITACIÓN
        # ====================================================

        try:

            invite = await canal.create_invite(
                max_age=0,
                max_uses=0,
                unique=False,
                reason=f"Invitación creada por {interaction.user}"
            )

        except discord.Forbidden:

            return await interaction.followup.send(
                "❌ No tengo permiso para crear invitaciones."
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error creando invitación: {error}"
            )

            return await interaction.followup.send(
                "❌ Discord no permitió crear la invitación."
            )

        except Exception as error:

            print(
                f"❌ Error inesperado: {error}"
            )

            return await interaction.followup.send(
                "❌ Ocurrió un error creando la invitación."
            )

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="💜 ¡Estás invitado!",
            description=(
                f"## ✨ {interaction.guild.name}\n\n"
                "🎮 **Comunidad activa**\n"
                "💬 **Chat y buena onda**\n"
                "🎭 **Roles personalizados**\n"
                "🎉 **Eventos y actividades**\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔗 **Entrá al servidor:**\n"
                f"**{invite.url}**\n\n"
                "💜 ¡Te esperamos!"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        if interaction.guild.icon:
            embed.set_thumbnail(
                url=interaction.guild.icon.url
            )

        embed.set_footer(
            text=f"Invitación creada por {interaction.user.display_name}"
        )

        # ====================================================
        # ENVIAR
        # ====================================================

        await interaction.followup.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Invitacion(bot)
    )
