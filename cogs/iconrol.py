import aiohttp
import discord
from discord.ext import commands


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setroleicon", aliases=["icono_rol"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def set_role_icon(self, ctx, role: discord.Role, url: str = None):
        """Cambia el ícono de un rol usando una URL o una imagen adjunta.

        Uso: !setroleicon @Rol https://imagen.com/foto.png
             !setroleicon @Rol (con la imagen adjunta en el mensaje)
        """
        image_bytes = None

        # Opción 1: Obtener imagen si se subió como archivo adjunto
        if ctx.message.attachments:
            image_bytes = await ctx.message.attachments[0].read()

        # Opción 2: Descargar la imagen desde la URL proporcionada
        elif url:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                    else:
                        await ctx.send(
                            "❌ No se pudo descargar la imagen desde la URL provista."
                        )
                        return
        else:
            await ctx.send(
                "❌ Debes adjuntar una imagen o proporcionar una URL."
            )
            return

        # Aplicar el ícono al rol
        try:
            await role.edit(
                display_icon=image_bytes,
                reason=f"Ícono actualizado por {ctx.author}",
            )
            await ctx.send(
                f"✅ El ícono del rol **{role.name}** ha sido actualizado correctamente."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos para editar este rol (asegúrate de que mi rol esté por encima en la jerarquía)."
            )
        except discord.HTTPException as e:
            await ctx.send(
                f"❌ Error de Discord (recuerda que el servidor necesita **Boost Nivel 2** para íconos de rol): {e}"
            )


async def setup(bot):
    await bot.add_cog(Roles(bot))
