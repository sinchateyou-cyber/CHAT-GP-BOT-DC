import re
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands


class IconRol(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setroleicon",
        description="Cambia el icono de un rol usando un emoji estándar o personalizado."
    )
    @app_commands.describe(
        rol="El rol al que deseas cambiarle el icono.",
        emoji="El emoji que deseas asignar como icono (ej: 👑 o un emoji personalizado)."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def set_role_icon(
        self, 
        interaction: discord.Interaction, 
        rol: discord.Role, 
        emoji: str
    ):
        await interaction.response.defer()

        # 1. Verificar si el servidor soporta iconos en los roles (Requiere Nivel 2 de Boost)
        if "ROLE_ICONS" not in interaction.guild.features:
            await interaction.followup.send(
                "❌ Este servidor necesita **Nivel 2 de Server Boost** para poder usar iconos en los roles.",
                ephemeral=True
            )
            return

        # 2. Expresión regular para detectar si es un emoji personalizado (<:nombre:id> o <a:nombre:id>)
        custom_emoji_regex = r"<a?:(?P<name>\w+):(?P<id>\d+)>"
        match = re.match(custom_emoji_regex, emoji.strip())

        try:
            if match:
                # Si es un emoji personalizado, se descarga su imagen desde la CDN de Discord
                emoji_id = match.group("id")
                image_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"

                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status != 200:
                            await interaction.followup.send(
                                "❌ No se pudo descargar la imagen del emoji personalizado.",
                                ephemeral=True
                            )
                            return
                        image_data = await response.read()

                await rol.edit(display_icon=image_data)

            else:
                # Si es un emoji unicode (ejemplo: 👑, 🔥, 🚀)
                try:
                    await rol.edit(display_icon=emoji.strip())
                except discord.HTTPException:
                    # En caso de que se haya enviado texto plano que no sea un emoji válido
                    await interaction.followup.send(
                        "❌ El emoji ingresado no es válido. Asegúrate de enviar un emoji Unicode o uno de Discord.",
                        ephemeral=True
                    )
                    return

            # Crear embed de confirmación
            embed = discord.Embed(
                title="✅ Icono de rol actualizado",
                description=f"El icono del rol {rol.mention} ha sido actualizado correctamente.",
                color=discord.Color.green()
            )
            
            if match:
                embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{match.group('id')}.png")

            await interaction.followup.send(embed=embed)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos suficientes. Asegúrate de que mi rol esté por encima del rol que intentas editar.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Ocurrió un error insospechado al actualizar el rol: `{e}`",
                ephemeral=True
            )

    # Manejo de errores para cuando el usuario no tiene permisos
    @set_role_icon.error
    async def set_role_icon_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes el permiso de **Gestionar Roles** para usar este comando.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(IconRol(bot))
