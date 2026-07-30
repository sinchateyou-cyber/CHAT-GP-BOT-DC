import random
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
VERIFIED_ROLE_NAME = "Verificado"
UNVERIFIED_ROLE_NAME = "No Verificado"
# ============================================================
# MODAL DEL CAPTCHA
# ============================================================
class CaptchaModal(discord.ui.Modal, title="🛡️ Verificación"):
    respuesta = discord.ui.TextInput(
        label="Respuesta",
        placeholder="Escribí solamente el resultado",
        required=True,
        max_length=10
    )
    def __init__(
        self,
        member: discord.Member,
        number1: int,
        number2: int,
        operation: str,
        answer: int
    ):
        super().__init__()
        self.member = member
        self.answer = answer
        # Mostrar la operación matemática
        self.respuesta.label = (
            f"Resolvé: {number1} {operation} {number2} = ?"
        )
    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        # ====================================================
        # COMPROBAR USUARIO
        # ====================================================
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "❌ Este CAPTCHA no es para vos.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR RESPUESTA
        # ====================================================
        try:
            user_answer = int(
                self.respuesta.value.strip()
            )
        except ValueError:
            await interaction.response.send_message(
                "❌ Tenés que escribir un número válido.",
                ephemeral=True
            )
            return
        # ====================================================
        # RESPUESTA INCORRECTA
        # ====================================================
        if user_answer != self.answer:
            await interaction.response.send_message(
                "❌ **Respuesta incorrecta.**\n\n"
                "Volvé a presionar el botón "
                "**Verificarme** para obtener "
                "un nuevo CAPTCHA.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR SERVIDOR
        # ====================================================
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Este sistema solo funciona dentro "
                "de un servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # BUSCAR ROLES
        # ====================================================
        verified_role = discord.utils.get(
            guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        unverified_role = discord.utils.get(
            guild.roles,
            name=UNVERIFIED_ROLE_NAME
        )
        # ====================================================
        # CREAR ROL VERIFICADO
        # ====================================================
        if verified_role is None:
            try:
                verified_role = await guild.create_role(
                    name=VERIFIED_ROLE_NAME,
                    reason="Sistema de verificación del bot"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ No tengo permisos para crear "
                    "el rol `Verificado`.",
                    ephemeral=True
                )
                return
        # ====================================================
        # DAR ROL Y QUITAR NO VERIFICADO
        # ====================================================
        try:
            # Dar rol Verificado
            await self.member.add_roles(
                verified_role,
                reason="Usuario completó correctamente el CAPTCHA"
            )
            # Quitar rol No Verificado
            if unverified_role:
                if unverified_role in self.member.roles:
                    await self.member.remove_roles(
                        unverified_role,
                        reason="Usuario completó la verificación"
                    )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo administrar los roles.\n\n"
                "Asegurate de que el rol del bot esté "
                "por encima de `Verificado` y "
                "`No Verificado`.",
                ephemeral=True
            )
            return
        # ====================================================
        # VERIFICACIÓN COMPLETADA
        # ====================================================
        await interaction.response.send_message(
            "✅ **¡Verificación completada!**\n\n"
            "Ya estás verificado y tenés acceso al servidor.",
            ephemeral=True
        )
# ============================================================
# VIEW DEL BOTÓN
# ============================================================
class VerificationView(discord.ui.View):
    def __init__(self):
        # None = botón permanente
        super().__init__(
            timeout=None
        )
    # ========================================================
    # BOTÓN VERIFICARME
    # ========================================================
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
        # ====================================================
        # COMPROBAR SERVIDOR
        # ====================================================
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # BUSCAR USUARIO
        # ====================================================
        member = interaction.guild.get_member(
            interaction.user.id
        )
        if member is None:
            await interaction.response.send_message(
                "❌ No pude encontrar tu usuario.",
                ephemeral=True
            )
            return
        # ====================================================
        # BUSCAR ROL VERIFICADO
        # ====================================================
        verified_role = discord.utils.get(
            interaction.guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        # ====================================================
        # COMPROBAR SI YA ESTÁ VERIFICADO
        # ====================================================
        if verified_role:
            if verified_role in member.roles:
                await interaction.response.send_message(
                    "✅ Ya estás verificado.",
                    ephemeral=True
                )
                return
        # ====================================================
        # GENERAR CAPTCHA
        # ====================================================
        number1 = random.randint(
            1,
            20
        )
        number2 = random.randint(
            1,
            20
        )
        operation = random.choice(
            [
                "+",
                "-"
            ]
        )
        # ====================================================
        # CALCULAR RESPUESTA
        # ====================================================
        if operation == "+":
            answer = (
                number1 +
                number2
            )
        else:
            # Evitar resultados negativos
            if number2 > number1:
                number1, number2 = (
                    number2,
                    number1
                )
            answer = (
                number1 -
                number2
            )
        # ====================================================
        # MOSTRAR CAPTCHA
        # ====================================================
        await interaction.response.send_modal(
            CaptchaModal(
                member=member,
                number1=number1,
                number2=number2,
                operation=operation,
                answer=answer
            )
        )
# ============================================================
# COG DE VERIFICACIÓN
# ============================================================
class Verification(commands.Cog):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
    # ========================================================
    # COMANDO /VERIFICATION
    # ========================================================
    @app_commands.command(
        name="verification",
        description="Envía el panel de verificación."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def verification(
        self,
        interaction: discord.Interaction
    ):
        # ====================================================
        # EMBED
        # ====================================================
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "Para acceder al servidor, "
                "tenés que completar una pequeña "
                "verificación.\n\n"
                "Presioná el botón **Verificarme** "
                "y resolvé la operación matemática "
                "que aparecerá.\n\n"
                "🔒 Este sistema ayuda a proteger "
                "el servidor contra cuentas automatizadas."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Sistema de verificación"
        )
        # ====================================================
        # ENVIAR PANEL
        # ====================================================
        await interaction.channel.send(
            embed=embed,
            view=VerificationView()
        )
        # ====================================================
        # RESPONDER AL ADMIN
        # ====================================================
        await interaction.response.send_message(
            "✅ **Panel de verificación enviado correctamente.**",
            ephemeral=True
        )
# ============================================================
# SETUP DEL COG
# ============================================================
async def setup(
    bot
):
    await bot.add_cog(
        Verification(bot)
    )