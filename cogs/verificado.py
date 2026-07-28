import discord
from discord.ext import commands
class VerificacionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    # =========================
    # BOTÓN VERIFICAR
    # =========================
    @discord.ui.button(
        label="Verificarme",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="boton_verificacion"
    )
    async def verificar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild
        miembro = interaction.user
        # Buscar el rol Verificado
        rol = discord.utils.get(
            guild.roles,
            name="Verificado"
        )
        # Si no existe el rol
        if rol is None:
            await interaction.response.send_message(
                "❌ El rol `Verificado` no existe. "
                "Crealo primero en el servidor.",
                ephemeral=True
            )
            return
        # Si ya está verificado
        if rol in miembro.roles:
            await interaction.response.send_message(
                "✅ Ya estás verificado.",
                ephemeral=True
            )
            return
        # Dar el rol
        try:
            await miembro.add_roles(
                rol,
                reason="Usuario verificado mediante el botón."
            )
            await interaction.response.send_message(
                "✅ **¡Verificación completada!**\n"
                "Ahora ya podés acceder al servidor.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo darte el rol `Verificado`.\n"
                "Asegurate de que el rol del bot esté "
                "por encima del rol `Verificado`.",
                ephemeral=True
            )
class Verificacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # COMANDO VERIFICACIÓN
    # =========================
    @commands.command(name="verificacion")
    @commands.has_permissions(administrator=True)
    async def verificacion(self, ctx):
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "¡Bienvenido/a al servidor!\n\n"
                "Para acceder al resto del servidor, "
                "debes verificarte primero.\n\n"
                "Presioná el botón **✅ Verificarme** "
                "para obtener acceso."
            )
        )
        embed.add_field(
            name="📌 ¿Qué tengo que hacer?",
            value=(
                "1️⃣ Leé las reglas del servidor.\n"
                "2️⃣ Presioná **Verificarme**.\n"
                "3️⃣ Recibí el rol `Verificado`.\n"
                "4️⃣ Disfrutá del servidor."
            ),
            inline=False
        )
        embed.set_footer(
            text="Sistema de verificación"
        )
        await ctx.send(
            embed=embed,
            view=VerificacionView()
        )
    # =========================
    # ERROR DEL COMANDO
    # =========================
    @verificacion.error
    async def verificacion_error(
        self,
        ctx,
        error
    ):
        if isinstance(
            error,
            commands.MissingPermissions
        ):
            await ctx.send(
                f"❌ {ctx.author.mention}, "
                "necesitás permisos de administrador "
                "para usar este comando.",
                delete_after=5
            )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Verificacion(bot)
    )
    # Mantener el botón funcionando
    # después de reiniciar el bot
    bot.add_view(
        VerificacionView()
    )