import discord
from discord.ext import commands
# ============================================================
# OWNER PRINCIPAL
# ============================================================
MAIN_OWNER_ID = 1460867297500594266
# ============================================================
# COG AVATAR
# ============================================================
class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ========================================================
    # /avatar
    # s!avatar
    # ========================================================
    @commands.hybrid_command(
        name="avatar",
        description="Muestra el avatar de un usuario."
    )
    async def avatar(
        self,
        ctx: commands.Context,
        usuario: discord.Member = None
    ):
        if usuario is None:
            usuario = ctx.author
        embed = discord.Embed(
            title=f"🖼️ Avatar de {usuario.display_name}",
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )
        embed.set_image(
            url=usuario.display_avatar.url
        )
        embed.set_footer(
            text=f"ID: {usuario.id}"
        )
        await ctx.send(
            embed=embed
        )
    # ========================================================
    # /setavatar
    # s!setavatar
    # ========================================================
    @commands.hybrid_command(
        name="setavatar",
        description="Cambia la foto de perfil del bot."
    )
    async def setavatar(
        self,
        ctx: commands.Context,
        imagen: discord.Attachment
    ):
        if ctx.author.id != MAIN_OWNER_ID:
            await ctx.send(
                "❌ Solo el owner principal del bot puede usar este comando.",
                ephemeral=bool(ctx.interaction)
            )
            return
        if (
            not imagen.content_type
            or not imagen.content_type.startswith("image/")
        ):
            await ctx.send(
                "❌ El archivo debe ser una imagen.",
                ephemeral=bool(ctx.interaction)
            )
            return
        try:
            image_data = await imagen.read()
            await self.bot.user.edit(
                avatar=image_data
            )
            await ctx.send(
                "✅ **Foto de perfil actualizada correctamente.**",
                ephemeral=bool(ctx.interaction)
            )
        except discord.HTTPException as error:
            await ctx.send(
                f"❌ No se pudo cambiar la foto de perfil.\n"
                f"Error: `{error}`",
                ephemeral=bool(ctx.interaction)
            )
        except Exception as error:
            await ctx.send(
                f"❌ Ocurrió un error inesperado.\n"
                f"Error: `{error}`",
                ephemeral=bool(ctx.interaction)
            )
    # ========================================================
    # /setname
    # s!setname
    # ========================================================
    @commands.hybrid_command(
        name="setname",
        description="Cambia el nombre de usuario del bot."
    )
    async def setname(
        self,
        ctx: commands.Context,
        nombre: str
    ):
        if ctx.author.id != MAIN_OWNER_ID:
            await ctx.send(
                "❌ Solo el owner principal del bot puede usar este comando.",
                ephemeral=bool(ctx.interaction)
            )
            return
        if len(nombre) < 2 or len(nombre) > 32:
            await ctx.send(
                "❌ El nombre debe tener entre 2 y 32 caracteres.",
                ephemeral=bool(ctx.interaction)
            )
            return
        try:
            await self.bot.user.edit(
                username=nombre
            )
            await ctx.send(
                f"✅ El nombre del bot cambió a **{nombre}**.",
                ephemeral=bool(ctx.interaction)
            )
        except discord.HTTPException as error:
            await ctx.send(
                f"❌ No se pudo cambiar el nombre.\n"
                f"Error: `{error}`",
                ephemeral=bool(ctx.interaction)
            )
        except Exception as error:
            await ctx.send(
                f"❌ Ocurrió un error inesperado.\n"
                f"Error: `{error}`",
                ephemeral=bool(ctx.interaction)
            )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Avatar(bot)
    )