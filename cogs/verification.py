import random
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
VERIFIED_ROLE_NAME = "Verificado"
UNVERIFIED_ROLE_NAME = "No Verificado"
VERIFICATION_CHANNEL_NAME = "・verificacion"
# ============================================================
# CAPTCHA
# ============================================================
class CaptchaModal(discord.ui.Modal):
    def __init__(
        self,
        member: discord.Member,
        number1: int,
        number2: int,
        operation: str,
        answer: int
    ):
        super().__init__(
            title="🛡️ Verificación"
        )
        self.member = member
        self.answer = answer
        self.respuesta = discord.ui.TextInput(
            label=f"Resolvé: {number1} {operation} {number2} = ?",
            placeholder="Escribí solamente el resultado",
            required=True,
            max_length=10
        )
        self.add_item(
            self.respuesta
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
                "❌ Escribí solamente un número.",
                ephemeral=True
            )
            return
        # ====================================================
        # CAPTCHA INCORRECTO
        # ====================================================
        if user_answer != self.answer:
            await interaction.response.send_message(
                "❌ **Respuesta incorrecta.**\n\n"
                "Volvé a presionar **Verificarme** "
                "para recibir otro CAPTCHA.",
                ephemeral=True
            )
            return
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
        if verified_role is None:
            await interaction.response.send_message(
                "❌ No existe el rol `Verificado`.",
                ephemeral=True
            )
            return
        # ====================================================
        # DAR VERIFICADO
        # ====================================================
        try:
            await self.member.add_roles(
                verified_role,
                reason="CAPTCHA completado correctamente"
            )
            # =================================================
            # QUITAR NO VERIFICADO
            # =================================================
            if unverified_role is not None:
                if unverified_role in self.member.roles:
                    await self.member.remove_roles(
                        unverified_role,
                        reason="Usuario verificado"
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
        # ÉXITO
        # ====================================================
        await interaction.response.send_message(
            "✅ **¡Verificación completada!**\n\n"
            "Ahora podés ver los canales del servidor.",
            ephemeral=True
        )
# ============================================================
# PANEL DE VERIFICACIÓN
# ============================================================
class VerificationView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=None
        )
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
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona "
                "dentro de un servidor.",
                ephemeral=True
            )
            return
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
        # COMPROBAR SI YA ESTÁ VERIFICADO
        # ====================================================
        verified_role = discord.utils.get(
            interaction.guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        if verified_role is not None:
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
# COG
# ============================================================
class Verification(
    commands.Cog
):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
    # ========================================================
    # /VERIFICATION SETUP
    # ========================================================
    verification_group = app_commands.Group(
        name="verification",
        description="Sistema de verificación del servidor."
    )
    @verification_group.command(
        name="setup",
        description="Configura el sistema de verificación."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def setup_verification(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo funciona dentro "
                "de un servidor.",
                ephemeral=True
            )
            return
        await interaction.response.defer(
            ephemeral=True
        )
        # ====================================================
        # COMPROBAR PERMISOS DEL BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.followup.send(
                "❌ No pude obtener información del bot.",
                ephemeral=True
            )
            return
        if not bot_member.guild_permissions.manage_roles:
            await interaction.followup.send(
                "❌ Necesito el permiso **Gestionar Roles**.",
                ephemeral=True
            )
            return
        if not bot_member.guild_permissions.manage_channels:
            await interaction.followup.send(
                "❌ Necesito el permiso **Gestionar Canales**.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR ROL VERIFICADO
        # ====================================================
        verified_role = discord.utils.get(
            guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        if verified_role is None:
            verified_role = await guild.create_role(
                name=VERIFIED_ROLE_NAME,
                reason="Configuración del sistema de verificación"
            )
        # ====================================================
        # CREAR ROL NO VERIFICADO
        # ====================================================
        unverified_role = discord.utils.get(
            guild.roles,
            name=UNVERIFIED_ROLE_NAME
        )
        if unverified_role is None:
            unverified_role = await guild.create_role(
                name=UNVERIFIED_ROLE_NAME,
                reason="Configuración del sistema de verificación"
            )
        # ====================================================
        # POSICIÓN DE ROLES
        # ====================================================
        try:
            # El bot debe estar por encima
            # de los roles que administra
            if verified_role.position >= bot_member.top_role.position:
                await interaction.followup.send(
                    "❌ El rol del bot debe estar por encima "
                    "de `Verificado`.",
                    ephemeral=True
                )
                return
            if unverified_role.position >= bot_member.top_role.position:
                await interaction.followup.send(
                    "❌ El rol del bot debe estar por encima "
                    "de `No Verificado`.",
                    ephemeral=True
                )
                return
        except Exception:
            pass
        # ====================================================
        # CREAR CANAL DE VERIFICACIÓN
        # ====================================================
        verification_channel = discord.utils.get(
            guild.text_channels,
            name=VERIFICATION_CHANNEL_NAME
        )
        if verification_channel is None:
            overwrites = {
                guild.default_role:
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=False
                    ),
                unverified_role:
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=False
                    ),
                verified_role:
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=False
                    ),
                bot_member:
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        embed_links=True
                    )
            }
            verification_channel = await guild.create_text_channel(
                name=VERIFICATION_CHANNEL_NAME,
                overwrites=overwrites,
                reason="Canal del sistema de verificación"
            )
        else:
            # =================================================
            # ACTUALIZAR PERMISOS DEL CANAL
            # =================================================
            await verification_channel.set_permissions(
                unverified_role,
                view_channel=True,
                send_messages=False
            )
            await verification_channel.set_permissions(
                verified_role,
                view_channel=True,
                send_messages=False
            )
            await verification_channel.set_permissions(
                bot_member,
                view_channel=True,
                send_messages=True,
                embed_links=True
            )
        # ====================================================
        # OCULTAR CANALES A NO VERIFICADOS
        # ====================================================
        channels_hidden = 0
        for channel in guild.channels:
            # No modificar el canal de verificación
            if channel.id == verification_channel.id:
                continue
            # No modificar categorías
            if isinstance(
                channel,
                discord.CategoryChannel
            ):
                continue
            try:
                await channel.set_permissions(
                    unverified_role,
                    view_channel=False
                )
                channels_hidden += 1
            except discord.Forbidden:
                continue
            except discord.HTTPException:
                continue
        # ====================================================
        # ENVIAR PANEL
        # ====================================================
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "### Bienvenido al servidor\n\n"
                "Para acceder a los canales del servidor "
                "tenés que completar una pequeña verificación.\n\n"
                "🔐 **¿Cómo verificarse?**\n"
                "1. Presioná **Verificarme**.\n"
                "2. Resolvé la operación matemática.\n"
                "3. Recibí el rol **Verificado**.\n"
                "4. Accedé automáticamente a los canales.\n\n"
                "🔒 Este sistema ayuda a proteger "
                "el servidor contra cuentas automatizadas."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Sistema de verificación"
        )
        try:
            await verification_channel.send(
                embed=embed,
                view=VerificationView()
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "⚠️ La configuración se realizó, "
                "pero no puedo enviar mensajes en "
                f"{verification_channel.mention}.",
                ephemeral=True
            )
            return
        # ====================================================
        # RESULTADO
        # ====================================================
        await interaction.followup.send(
            "✅ **Sistema de verificación configurado.**\n\n"
            f"📌 Canal: {verification_channel.mention}\n"
            f"👤 Rol sin verificar: `{UNVERIFIED_ROLE_NAME}`\n"
            f"✅ Rol verificado: `{VERIFIED_ROLE_NAME}`\n"
            f"🔒 Canales restringidos: `{channels_hidden}`\n\n"
            "Los usuarios con `No Verificado` "
            "solo podrán ver el canal de verificación.",
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Verification(bot)
    )
    # Registrar botones persistentes
    bot.add_view(
        VerificationView()
    )