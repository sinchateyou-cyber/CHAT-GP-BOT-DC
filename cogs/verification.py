import random
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
VERIFIED_ROLE_NAME = "Verificado"
UNVERIFIED_ROLE_NAME = "No Verificado"
MAX_ATTEMPTS = 3
CAPTCHA_TIMEOUT = 60
# ============================================================
# MODAL DEL CAPTCHA
# ============================================================
class CaptchaModal(discord.ui.Modal, title="🛡️ Verificación"):
    respuesta = discord.ui.TextInput(
        label="Resolvé la operación matemática",
        placeholder="Escribí solamente el resultado",
        required=True,
        max_length=10
    )
    def __init__(self, member: discord.Member, number1: int, number2: int, operation: str, answer: int):
        super().__init__()
        self.member = member
        self.number1 = number1
        self.number2 = number2
        self.operation = operation
        self.answer = answer
    async def on_submit(self, interaction: discord.Interaction):
        # Evitar que otro usuario use el CAPTCHA
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "❌ Este CAPTCHA no es para vos.",
                ephemeral=True
            )
            return
        try:
            user_answer = int(self.respuesta.value.strip())
        except ValueError:
            await interaction.response.send_message(
                "❌ Tenés que escribir un número válido.",
                ephemeral=True
            )
            return
        # CAPTCHA incorrecto
        if user_answer != self.answer:
            await interaction.response.send_message(
                "❌ **Respuesta incorrecta.**\n"
                "Volvé a presionar el botón para intentar nuevamente.",
                ephemeral=True
            )
            return
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return
        verified_role = discord.utils.get(
            guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        unverified_role = discord.utils.get(
            guild.roles,
            name=UNVERIFIED_ROLE_NAME
        )
        # Crear rol Verificado si no existe
        if verified_role is None:
            try:
                verified_role = await guild.create_role(
                    name=VERIFIED_ROLE_NAME,
                    reason="Sistema de verificación del bot"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ No tengo permisos para crear el rol `Verificado`.",
                    ephemeral=True
                )
                return
        # Agregar rol Verificado
        try:
            await self.member.add_roles(
                verified_role,
                reason="Usuario completó correctamente el CAPTCHA"
            )
            # Quitar No Verificado
            if unverified_role and unverified_role in self.member.roles:
                await self.member.remove_roles(
                    unverified_role,
                    reason="Usuario verificado"
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo administrar los roles. "
                "Revisá que mi rol esté por encima de `Verificado`.",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            "✅ **¡Verificación completada!**\n"
            "Ya tenés acceso al servidor.",
            ephemeral=True
        )
# ============================================================
# BOTÓN DE VERIFICACIÓN
# ============================================================
class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(
        label="Verificarme",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="verification_button"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        member = interaction.guild.get_member(
            interaction.user.id
        )
        if member is None:
            await interaction.response.send_message(
                "❌ No pude encontrar tu usuario.",
                ephemeral=True
            )
            return
        verified_role = discord.utils.get(
            interaction.guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        # Ya está verificado
        if verified_role and verified_role in member.roles:
            await interaction.response.send_message(
                "✅ Ya estás verificado.",
                ephemeral=True
            )
            return
        # Generar CAPTCHA
        number1 = random.randint(1, 20)
        number2 = random.randint(1, 20)
        operation = random.choice([
            "+",
            "-"
        ])
        if operation == "+":
            answer = number1 + number2
        else:
            # Evitar resultados negativos
            if number2 > number1:
                number1, number2 = number2, number1
            answer = number1 - number2
        await interaction.response.send_modal(
            CaptchaModal(
                member,
                number1,
                number2,
                operation,
                answer
            )
        )
# ============================================================
# COG
# ============================================================
class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # --------------------------------------------------------
    # COMANDO /VERIFICATION
    # --------------------------------------------------------
    @app_commands.command(
        name="verification",
        description="Envía el panel de verificación del servidor."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def verification(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "Para acceder al servidor, tenés que completar "
                "una pequeña verificación.\n\n"
                "Presioná el botón **Verificarme** y resolvé "
                "la operación matemática.\n\n"
                "🔒 Esto ayuda a proteger el servidor contra "
                "cuentas automatizadas."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Sistema de verificación"
        )
        await interaction.channel.send(
            embed=embed,
            view=VerificationView()
        )
        await interaction.response.send_message(
            "✅ Panel de verificación enviado.",
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(Verification(bot))