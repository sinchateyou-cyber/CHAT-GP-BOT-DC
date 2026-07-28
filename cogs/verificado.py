import discord
from discord import app_commands
from discord.ext import commands
# =========================
# VISTA DE VERIFICACIÓN
# =========================
class VerificacionView(discord.ui.View):
    def __init__(self):
        super().__init__(
            timeout=None
        )
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
        # =========================
        # BUSCAR ROL VERIFICADO
        # =========================
        rol = discord.utils.get(
            guild.roles,
            name="Verificado"
        )
        # =========================
        # SI NO EXISTE EL ROL
        # =========================
        if rol is None:
            await interaction.response.send_message(
                "❌ El rol `Verificado` no existe.\n"
                "Crealo primero en el servidor.",
                ephemeral=True
            )
            return
        # =========================
        # SI YA ESTÁ VERIFICADO
        # =========================
        if rol in miembro.roles:
            await interaction.response.send_message(
                "✅ Ya estás verificado.",
                ephemeral=True
            )
            return
        # =========================
        # COMPROBAR JERARQUÍA DEL BOT
        # =========================
        if (
            guild.me
            and rol >= guild.me.top_role
        ):
            await interaction.response.send_message(
                "❌ No puedo darte el rol `Verificado`.\n"
                "El rol del bot debe estar por encima "
                "del rol `Verificado`.",
                ephemeral=True
            )
            return
        # =========================
        # DAR ROL
        # =========================
        try:
            await miembro.add_roles(
                rol,
                reason=(
                    "Usuario verificado "
                    "mediante el botón."
                )
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
# =========================
# COG VERIFICACIÓN
# =========================
class Verificacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # COMANDO VERIFICACIÓN
    # =========================
    @app_commands.command(
        name="verificacion",
        description="Envía el panel de verificación."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def verificacion(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "¡Bienvenido/a al servidor!\n\n"
                "Para acceder al resto del servidor, "
                "debes verificarte primero.\n\n"
                "Presioná el botón **✅ Verificarme** "
                "para obtener acceso."
            ),
            color=discord.Color.green()
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
        await interaction.response.send_message(
            embed=embed,
            view=VerificacionView()
        )
    # =========================
    # ERROR DEL COMANDO
    # =========================
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            await interaction.response.send_message(
                f"❌ {interaction.user.mention}, "
                "necesitás permisos de administrador "
                "para usar este comando.",
                ephemeral=True
            )
        else:
            print(
                f"❌ Error en /verificacion: {error}"
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al ejecutar "
                    "el comando.",
                    ephemeral=True
                )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Verificacion(bot)
    )
    # =========================
    # MANTENER BOTÓN ACTIVO
    # =========================
    bot.add_view(
        VerificacionView()
    )