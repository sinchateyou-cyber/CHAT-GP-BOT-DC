import discord
from discord.ext import commands


class VerificacionView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verificarme",
        emoji="✅",
        style=discord.ButtonStyle.green,
        custom_id="boton_verificar"
    )
    async def verificar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        usuario = interaction.user

        # Buscar el rol Verificado
        rol = discord.utils.get(
            guild.roles,
            name="Verificado"
        )

        # Si el rol no existe
        if rol is None:

            await interaction.response.send_message(
                "❌ No existe el rol `Verificado` "
                "en este servidor.",
                ephemeral=True
            )

            return

        # Comprobar si ya tiene el rol
        if rol in usuario.roles:

            await interaction.response.send_message(
                "ℹ️ Ya estás verificado.",
                ephemeral=True
            )

            return

        # Comprobar posición del rol
        if rol >= guild.me.top_role:

            await interaction.response.send_message(
                "❌ No puedo asignar el rol "
                "`Verificado` porque mi rol está "
                "por debajo de él.",
                ephemeral=True
            )

            return

        try:

            await usuario.add_roles(
                rol,
                reason="Verificación mediante botón"
            )

            await interaction.response.send_message(
                "✅ ¡Te verificaste correctamente!",
                ephemeral=True
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para asignarte "
                "el rol.",
                ephemeral=True
            )


class Verificacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(
        administrator=True
    )
    async def verificacion(self, ctx):

        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "¡Bienvenido/a al servidor!\n\n"
                "Para acceder al servidor, "
                "presioná el botón **Verificarme** "
                "de abajo.\n\n"
                "✅ Recibirás automáticamente el rol "
                "**Verificado**."
            )
        )

        embed.set_footer(
            text="Sistema de verificación"
        )

        await ctx.send(
            embed=embed,
            view=VerificacionView()
        )


    @verificacion.error
    async def error_verificacion(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Solo los administradores "
                "pueden crear el panel."
            )

        else:

            print(
                f"❌ Error de verificación: {error}"
            )


async def setup(bot):

    await bot.add_cog(
        Verificacion(bot)
    )

    # Mantiene el botón funcionando
    # después de reiniciar el bot
    bot.add_view(
        VerificacionView()
    )