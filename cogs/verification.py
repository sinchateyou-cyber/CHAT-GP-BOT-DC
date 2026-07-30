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
        # RESPUESTA INCORRECTA
        # ====================================================
        if user_answer != self.answer:
            await interaction.response.send_message(
                "❌ **Respuesta incorrecta.**\n\n"
                "Presioná nuevamente **Verificarme** "
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
                "❌ El rol `Verificado` no existe.",
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
        # ====================================================
        # COMPROBAR SERVIDOR
        # ====================================================
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona "
                "dentro de un servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # OBTENER MIEMBRO
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
        # ABRIR CAPTCHA
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
    # EVENTO: USUARIO ENTRA
    # ========================================================
    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):
        # Buscar rol No Verificado
        unverified_role = discord.utils.get(
            member.guild.roles,
            name=UNVERIFIED_ROLE_NAME
        )
        if unverified_role is None:
            return
        # Si ya tiene Verificado, no hacer nada
        verified_role = discord.utils.get(
            member.guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        if verified_role is not None:
            if verified_role in member.roles:
                return
        # Dar rol No Verificado
        try:
            await member.add_roles(
                unverified_role,
                reason="Nuevo miembro - requiere verificación"
            )
        except discord.Forbidden:
            print(
                f"[VERIFICATION] No pude dar "
                f"No Verificado a {member}"
            )
        except discord.HTTPException as error:
            print(
                f"[VERIFICATION] Error: {error}"
            )
    # ========================================================
    # EVENTO: SE CREA UN CANAL
    # ========================================================
    @commands.Cog.listener()
    async def on_guild_channel_create(
        self,
        channel: discord.abc.GuildChannel
    ):
        guild = channel.guild
        # Buscar rol No Verificado
        unverified_role = discord.utils.get(
            guild.roles,
            name=UNVERIFIED_ROLE_NAME
        )
        if unverified_role is None:
            return
        # Si es el canal de verificación,
        # no ocultarlo
        if channel.name == VERIFICATION_CHANNEL_NAME:
            return
        # ====================================================
        # OCULTAR CANAL A NO VERIFICADOS
        # ====================================================
        try:
            await channel.set_permissions(
                unverified_role,
                view_channel=False
            )
            print(
                f"[VERIFICATION] Canal protegido: "
                f"{channel.name}"
            )
        except discord.Forbidden:
            print(
                f"[VERIFICATION] No tengo permisos "
                f"para configurar {channel.name}"
            )
        except discord.HTTPException as error:
            print(
                f"[VERIFICATION] Error: {error}"
            )
    # ========================================================
    # GRUPO /VERIFICATION
    # ========================================================
    verification_group = app_commands.Group(
        name="verification",
        description="Sistema de verificación."
    )
    # ========================================================
    # /VERIFICATION SETUP
    # ========================================================
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
                "❌ Este comando solo funciona "
                "dentro de un servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # DEFER
        # ====================================================
        await interaction.response.defer(
            ephemeral=True
        )
        # ====================================================
        # BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.followup.send(
                "❌ No pude obtener información del bot.",
                ephemeral=True
            )
            return
        # ====================================================
        # PERMISOS
        # ====================================================
        if not bot_member.guild_permissions.manage_roles:
            await interaction.followup.send(
                "❌ Necesito el permiso "
                "**Gestionar Roles**.",
                ephemeral=True
            )
            return
        if not bot_member.guild_permissions.manage_channels:
            await interaction.followup.send(
                "❌ Necesito el permiso "
                "**Gestionar Canales**.",
                ephemeral=True
            )
            return
        # ====================================================
        # ROL VERIFICADO
        # ====================================================
        verified_role = discord.utils.get(
            guild.roles,
            name=VERIFIED_ROLE_NAME
        )
        if verified_role is None:
            verified_role = await guild.create_role(
                name=VERIFIED_ROLE_NAME,
                reason="Sistema de verificación"
            )
        # ====================================================
        # ROL NO VERIFICADO
        # ====================================================
        unverified_role = discord.utils.get(
            guild.roles,
            name=UNVERIFIED_ROLE_NAME
        )
        if unverified_role is None:
            unverified_role = await guild.create_role(
                name=UNVERIFIED_ROLE_NAME,
                reason="Sistema de verificación"
            )
        # ====================================================
        # COMPROBAR POSICIÓN
        # ====================================================
        if verified_role.position >= bot_member.top_role.position:
            await interaction.followup.send(
                "❌ El rol del bot debe estar por encima "
                "del rol `Verificado`.",
                ephemeral=True
            )
            return
        if unverified_role.position >= bot_member.top_role.position:
            await interaction.followup.send(
                "❌ El rol del bot debe estar por encima "
                "del rol `No Verificado`.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR CANAL DE VERIFICACIÓN
        # ====================================================
        verification_channel = discord.utils.get(
            guild.text_channels,
            name=VERIFICATION_CHANNEL_NAME
        )
        if verification_channel is None:
            verification_channel = (
                await guild.create_text_channel(
                    name=VERIFICATION_CHANNEL_NAME,
                    reason="Sistema de verificación"
                )
            )
        # ====================================================
        # CONFIGURAR CANAL DE VERIFICACIÓN
        # ====================================================
        await verification_channel.set_permissions(
            guild.default_role,
            view_channel=True,
            send_messages=False
        )
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
        # OCULTAR TODOS LOS CANALES
        # ====================================================
        channels_protected = 0
        for channel in guild.channels:
            # Ignorar canal de verificación
            if channel.id == verification_channel.id:
                continue
            # No configurar categorías
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
                channels_protected += 1
            except discord.Forbidden:
                continue
            except discord.HTTPException:
                continue
        # ====================================================
        # PANEL
        # ====================================================
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "### ¡Bienvenido!\n\n"
                "Para acceder a los canales del servidor "
                "tenés que completar la verificación.\n\n"
                "🔐 **Proceso:**\n\n"
                "1️⃣ Presioná **Verificarme**.\n"
                "2️⃣ Resolvé la operación matemática.\n"
                "3️⃣ Recibí el rol **Verificado**.\n"
                "4️⃣ Accedé a todos los canales.\n\n"
                "🔒 Hasta verificarte, no podrás ver "
                "el resto del servidor."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Sistema de verificación"
        )
        # ====================================================
        # ENVIAR PANEL
        # ====================================================
        await verification_channel.send(
            embed=embed,
            view=VerificationView()
        )
        # ====================================================
        # RESULTADO
        # ====================================================
        await interaction.followup.send(
            "✅ **Sistema de verificación configurado.**\n\n"
            f"📌 Canal: {verification_channel.mention}\n"
            f"👤 Rol: `{UNVERIFIED_ROLE_NAME}`\n"
            f"✅ Rol: `{VERIFIED_ROLE_NAME}`\n"
            f"🔒 Canales protegidos: `{channels_protected}`\n\n"
            "Los nuevos usuarios recibirán "
            "`No Verificado` automáticamente.",
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
    # Registrar vista persistente
    bot.add_view(
        VerificationView()
    )