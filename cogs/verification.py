import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# ARCHIVOS
# ============================================================
DATA_FOLDER = "data"
VERIFICATION_FILE = (
    "data/verification.json"
)
# ============================================================
# FUNCIONES
# ============================================================
def ensure_data_folder():
    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )
def load_data():
    ensure_data_folder()
    if not os.path.exists(
        VERIFICATION_FILE
    ):
        return {}
    try:
        with open(
            VERIFICATION_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(
                file
            )
            if isinstance(
                data,
                dict
            ):
                return data
    except (
        json.JSONDecodeError,
        OSError
    ):
        pass
    return {}
def save_data(
    data
):
    ensure_data_folder()
    with open(
        VERIFICATION_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )
# ============================================================
# VIEW DE VERIFICACIÓN
# ============================================================
class VerificationView(
    discord.ui.View
):
    def __init__(
        self
    ):
        super().__init__(
            timeout=None
        )
    @discord.ui.button(
        label="Verificarme",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="verificacion_definitiva"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return
        guild = interaction.guild
        member = guild.get_member(
            interaction.user.id
        )
        if member is None:
            await interaction.response.send_message(
                "❌ No pude encontrar tu usuario en el servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # BUSCAR ROL VERIFICADO
        # ====================================================
        role = discord.utils.get(
            guild.roles,
            name="Verificado"
        )
        if role is None:
            await interaction.response.send_message(
                "❌ El rol `Verificado` no existe.\n"
                "Pedile a un administrador que ejecute "
                "`/verification setup`.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR SI YA ESTÁ VERIFICADO
        # ====================================================
        if role in member.roles:
            await interaction.response.send_message(
                "✅ Ya estás verificado.",
                ephemeral=True
            )
            return
        # ====================================================
        # ASIGNAR ROL
        # ====================================================
        try:
            await member.add_roles(
                role,
                reason="Verificación mediante botón."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No pude asignarte el rol `Verificado`.\n"
                "Revisá que el rol del bot esté por encima "
                "del rol `Verificado`.",
                ephemeral=True
            )
            return
        # ====================================================
        # GUARDAR VERIFICACIÓN
        # ====================================================
        data = load_data()
        guild_id = str(
            guild.id
        )
        user_id = str(
            member.id
        )
        if guild_id not in data:
            data[guild_id] = {
                "verified_users": {}
            }
        if "verified_users" not in data[guild_id]:
            data[guild_id]["verified_users"] = {}
        data[guild_id]["verified_users"][user_id] = {
            "username":
                str(
                    member
                ),
            "display_name":
                member.display_name,
            "timestamp":
                discord.utils.utcnow().isoformat()
        }
        save_data(
            data
        )
        await interaction.response.send_message(
            "✅ **Verificación completada.**\n"
            "🎉 Ahora podés ver los canales del servidor.",
            ephemeral=True
        )
# ============================================================
# COG VERIFICATION
# ============================================================
class Verification(
    commands.Cog
):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        ensure_data_folder()
        # Botón persistente
        self.bot.add_view(
            VerificationView()
        )
    # ========================================================
    # /verification setup
    # ========================================================
    verification_group = app_commands.Group(
        name="verification",
        description="Configura el sistema de verificación."
    )
    @verification_group.command(
        name="setup",
        description="Configura el servidor para usar verificación."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        administrator=True
    )
    async def verification_setup(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild
        await interaction.response.defer(
            ephemeral=True
        )
        # ====================================================
        # COMPROBAR PERMISOS DEL BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.followup.send(
                "❌ No pude obtener los permisos del bot.",
                ephemeral=True
            )
            return
        if not bot_member.guild_permissions.administrator:
            await interaction.followup.send(
                "❌ Necesito el permiso **Administrador** "
                "para configurar automáticamente la verificación.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR / BUSCAR ROL VERIFICADO
        # ====================================================
        verified_role = discord.utils.get(
            guild.roles,
            name="Verificado"
        )
        if verified_role is None:
            verified_role = await guild.create_role(
                name="Verificado",
                color=discord.Color.green(),
                reason="Sistema de verificación"
            )
        # ====================================================
        # CREAR / BUSCAR CATEGORÍA
        # ====================================================
        category = discord.utils.get(
            guild.categories,
            name="VERIFICACIÓN"
        )
        if category is None:
            category = await guild.create_category(
                name="VERIFICACIÓN",
                reason="Sistema de verificación"
            )
        # ====================================================
        # CREAR / BUSCAR CANAL REGLAS
        # ====================================================
        rules_channel = discord.utils.get(
            guild.text_channels,
            name="reglas"
        )
        if rules_channel is None:
            rules_channel = await guild.create_text_channel(
                name="reglas",
                category=category,
                reason="Sistema de verificación"
            )
        # ====================================================
        # CREAR / BUSCAR CANAL VERIFICACIÓN
        # ====================================================
        verification_channel = discord.utils.get(
            guild.text_channels,
            name="verificacion"
        )
        if verification_channel is None:
            verification_channel = await guild.create_text_channel(
                name="verificacion",
                category=category,
                reason="Sistema de verificación"
            )
        # ====================================================
        # PERMISOS DE CATEGORÍA
        # ====================================================
        # @everyone NO puede ver canales normales
        await category.set_permissions(
            guild.default_role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        # Rol Verificado
        await category.set_permissions(
            verified_role,
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
        # ====================================================
        # PERMISOS DEL CANAL REGLAS
        # ====================================================
        await rules_channel.set_permissions(
            guild.default_role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        await rules_channel.set_permissions(
            verified_role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        # ====================================================
        # PERMISOS DEL CANAL VERIFICACIÓN
        # ====================================================
        await verification_channel.set_permissions(
            guild.default_role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        await verification_channel.set_permissions(
            verified_role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        # ====================================================
        # BLOQUEAR @EVERYONE EN TODOS LOS DEMÁS CANALES
        # ====================================================
        for channel in guild.channels:
            if channel in (
                rules_channel,
                verification_channel
            ):
                continue
            try:
                await channel.set_permissions(
                    guild.default_role,
                    view_channel=False
                )
            except discord.Forbidden:
                continue
            except discord.HTTPException:
                continue
        # ====================================================
        # GUARDAR CONFIGURACIÓN
        # ====================================================
        data = load_data()
        guild_id = str(
            guild.id
        )
        data[guild_id] = {
            "verified_role_id":
                verified_role.id,
            "rules_channel_id":
                rules_channel.id,
            "verification_channel_id":
                verification_channel.id,
            "setup_completed":
                True
        }
        save_data(
            data
        )
        # ====================================================
        # PUBLICAR REGLAS
        # ====================================================
        rules_embed = discord.Embed(
            title="📜 Reglas del servidor",
            description=(
                "**1.** Respetá a todos los miembros.\n\n"
                "**2.** No hagas spam ni flood.\n\n"
                "**3.** No compartas contenido ilegal o malicioso.\n\n"
                "**4.** No hagas publicidad sin permiso.\n\n"
                "**5.** Usá correctamente cada canal.\n\n"
                "**6.** Respetá al equipo de moderación.\n\n"
                "Al aceptar las reglas confirmás que "
                "las leíste y aceptás cumplirlas."
            ),
            color=discord.Color.blurple()
        )
        try:
            await rules_channel.send(
                embed=rules_embed
            )
        except discord.HTTPException:
            pass
        # ====================================================
        # PUBLICAR VERIFICACIÓN
        # ====================================================
        verification_embed = discord.Embed(
            title="✅ Verificación",
            description=(
                "Para acceder al resto del servidor, "
                "presioná el botón **Verificarme**.\n\n"
                "🔒 Los usuarios no verificados solamente "
                "pueden ver este canal y el canal de reglas.\n\n"
                "🔓 Después de verificarte podrás acceder "
                "a los demás canales."
            ),
            color=discord.Color.green()
        )
        try:
            await verification_channel.send(
                embed=verification_embed,
                view=VerificationView()
            )
        except discord.HTTPException:
            pass
        # ====================================================
        # RESPUESTA
        # ====================================================
        await interaction.followup.send(
            "✅ **Sistema de verificación configurado.**\n\n"
            f"📜 Reglas: {rules_channel.mention}\n"
            f"✅ Verificación: {verification_channel.mention}\n"
            f"👤 Rol: {verified_role.mention}\n\n"
            "🔒 Los usuarios no verificados no podrán ver "
            "los demás canales del servidor.",
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot
):
    await bot.add_cog(
        Verification(
            bot
        )
    )