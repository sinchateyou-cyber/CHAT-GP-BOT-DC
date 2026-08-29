import aiohttp
import discord
from discord.ext import commands


class IconRol(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="iconrol", aliases=["setroleicon", "icono_rol"])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def iconrol(self, ctx: commands.Context, role: discord.Role, url: str = None):
        """Cambia el icono de un rol mediante una URL o imagen adjunta.
        
        Uso:
            s!iconrol @Rol https://link.com/imagen.png
            s!iconrol @Rol (con una imagen adjunta)
        """
        image_bytes = None

        # 1. Verificar si hay un archivo adjunto en el mensaje
        if ctx.message.attachments:
            image_bytes = await ctx.message.attachments[0].read()

        # 2. Si no hay archivo adjunto, intentar descargar desde la URL
        elif url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            image_bytes = await response.read()
                        else:
                            await ctx.send(
                                "❌ No se pudo descargar la imagen. Verifica que la URL sea válida.",
                                delete_after=10
                            )
                            return
            except Exception as e:
                await ctx.send(
                    f"❌ Error al intentar conectar con la URL: {e}",
                    delete_after=10
                )
                return
        else:
            await ctx.send(
                "❌ Debes adjuntar una imagen al mensaje o indicar una URL válida.",
                delete_after=10
            )
            return

        # 3. Aplicar el icono al rol en Discord
        try:
            await role.edit(
                display_icon=image_bytes,
                reason=f"Icono modificado por {ctx.author} ({ctx.author.id})"
            )
            await ctx.send(
                f"✅ El icono del rol **{role.name}** se ha actualizado correctamente."
            )

        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos suficientes para editar este rol. Asegúrate de que el rol del bot esté por encima del rol a modificar.",
                delete_after=10
            )

        except discord.HTTPException as error:
            await ctx.send(
                f"❌ Error de Discord: {error.text}\n*(Recuerda que el servidor necesita tener **Nivel 2 de Boost** para usar iconos de roles)*",
                delete_after=12
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(IconRol(bot))
