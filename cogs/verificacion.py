import discord
from discord.ext import commands


class VerificacionView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=None
        )


    @discord.ui.button(
        label="Verificar",
        emoji="✅",
        style=discord.ButtonStyle.green
    )
    async def verificar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        rol = discord.utils.get(
            interaction.guild.roles,
            name="Verificado"
        )

        if rol is None:
            await interaction.response.send_message(
                "❌ No existe el rol `Verificado`.",
                ephemeral=True
            )
            return

        if rol in interaction.user.roles:
            await interaction.response.send_message(
                "ℹ️ Ya estás verificado.",
                ephemeral=True
            )
            return

        await interaction.user.add_roles(
            rol
        )

        await interaction.response.send_message(
            "✅ ¡Te verificaste correctamente!",
            ephemeral=True
        )


class Verificacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def verificacion(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="✅ Verificación",
            description=(
                "Presioná el botón de abajo "
                "para verificarte."
            )
        )

        await ctx.send(
            embed=embed,
            view=VerificacionView()
        )


async def setup(bot):
    await bot.add_cog(
        Verificacion(bot)
    )