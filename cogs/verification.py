import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
VERIFICATION_FILE = "data/verification.json"
VERIFIED_ROLE_NAME = "Verificado"
RULES_CHANNEL_NAME = "reglas"
VERIFICATION_CHANNEL_NAME = "verificacion"
VERIFICATION_CATEGORY_NAME = "VERIFICACIÓN"
# ============================================================
# FUNCIONES DE DATOS
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
            data = json.load(file)
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
def save_data(data):
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
# BUSCAR ROL VERIFICADO
# ============================================================
def get_verified_role(guild):
    return discord.utils.get(
        guild.roles,
        name=VERIFIED_ROLE_NAME
    )
# ============================================================
# CONFIGURAR PERMISOS
# ============================================================
async def configure_verification_permissions(
    guild,
    verified_role,
    rules_channel,
    verification_channel
):
    for channel in guild.channels:
        # ====================================================
        # CATEGORÍAS
        # ====================================================
        if isinstance(
            channel,
            discord.CategoryChannel
        ):
            # La categoría de verificación debe ser pública
            if channel.id == rules_channel.category_id:
                try:
                    await channel.set_permissions(
                        guild.default_role,
                        view_channel=True
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException
                ):
                    pass
                try:
                    await channel.set_permissions(
                        verified_role,
                        view_channel=True
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException
                ):
                    pass
            else:
                # Todas las demás categorías
                # quedan ocultas para @everyone
                try:
                    await channel.set_permissions(
                        guild.default_role,
                        view_channel=False
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException
                ):
                    pass
                # Verificado puede verlas
                try:
                    await channel.set_permissions(
                        verified_role,
                        view_channel=True
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException
                ):
                    pass
            continue
        # ====================================================
        # CANAL REGLAS
        # ====================================================
        if channel.id == rules_channel.id:
            try:
                await channel.set_permissions(
                    guild.default_role,
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )
            except (
                discord.Forbidden,
                discord.HTTPException
            ):
                pass
            try:
                await channel.set_permissions(
                    verified_role,
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )
            except (
                discord.Forbidden,
                discord.HTTPException
            ):
                pass
            continue
        # ====================================================
        # CANAL VERIFICACIÓN
        # ====================================================
        if channel.id == verification_channel.id:
            try:
                await channel.set_permissions(
                    guild.default_role,
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )
            except (
                discord.Forbidden,
                discord.HTTPException
            ):
                pass
            try:
                await channel.set_permissions(
                    verified_role,
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True
                )
            except (
                discord.Forbidden,
                discord.HTTPException
            ):
                pass
            continue
        # ====================================================
        # TODOS LOS DEMÁS CANALES
        # ====================================================
        # @everyone NO VE
        try:
            await channel.set_permissions(
                guild.default_role,
                view_channel=False
            )
        except (
            discord.Forbidden,
            discord.HTTPException
        ):
            pass
        # Verificado SÍ VE
        try:
            await channel.set_permissions(
                verified_role,
                view_channel=True
            )
        except (
            discord.Forbidden,
            discord.HTTPException
        ):
            pass
# ============================================================
# BOTÓN DE VERIFICACIÓN
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
        custom_id="verificacion_definitiva"
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
        guild = interaction.guild
        # ====================================================
        # BUSCAR MIEMBRO
        # ====================================================
        member = guild.get_member(
            interaction.user.id
        )
        if member is None:
            try:
                member = await guild.fetch_member(
                    interaction.user.id
                )
            except (
                discord.NotFound,
                discord.HTTPException
            ):
                await interaction.response.send_message(
                    "❌ No pude encontrar tu usuario en el servidor.",
                    ephemeral=True
                )
                return
        # ====================================================
        # BUSCAR ROL VERIFICADO
        # ====================================================
        verified_role = get_verified_role(
            guild
        )
        if verified_role is None:
            await interaction.response.send_message(
                "❌ El rol `Verificado` no existe.\n\n"
                "Un administrador debe ejecutar "
                "`/verification setup`.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.response.send_message(
                "❌ No pude comprobar los permisos del bot.",
                ephemeral=True
            )
            return
        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ El bot necesita el permiso "
                "**Administrar roles**.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR POSICIÓN DEL ROL
        # ====================================================
        if verified_role >= bot_member.top_role:
            await interaction.response.send_message(
                "❌ No puedo asignarte el rol `Verificado`.\n\n"
                "Mové el rol **Verificado** por debajo "
                "del rol más alto del bot.",
                ephemeral=True
            )
            return
        # ====================================================
        # YA ESTÁ VERIFICADO
        # ====================================================
        if verified_role in member.roles:
            await interaction.response.send_message(
                "✅ Ya estás verificado.\n\n"
                "Si todavía no ves los canales, "
                "un administrador debe ejecutar "
                "`/verification setup` nuevamente.",
                ephemeral=True
            )
            return
        # ====================================================
        # ASIGNAR ÚNICAMENTE VERIFICADO
        # ====================================================
        try:
            await member.add_roles(
                verified_role,
                reason="Verificación mediante botón."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No pude asignarte el rol `Verificado`.\n\n"
                "Revisá que el rol `Verificado` esté "
                "por debajo del rol del bot.",
                ephemeral=True
            )
            return
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Discord rechazó la asignación del rol.",
                ephemeral=True
            )
            return
        # ====================================================
        # GUARDAR DATOS
        # ====================================================
        data = load_data()
        guild_id = str(
            guild.id
        )
        user_id = str(
            member.id
        )
        if guild_id not in data:
            data[guild_id] = {}
        if "verified_users" not in data[guild_id]:
            data[guild_id][
                "verified_users"
            ] = {}
        data[guild_id][
            "verified_users"
        ][user_id] = {
            "username":
                str(member),
            "display_name":
                member.display_name,
            "timestamp":
                discord.utils.utcnow().isoformat()
        }
        data[guild_id][
            "verified_role_id"
        ] = verified_role.id
        save_data(
            data
        )
        # ====================================================
        # CONFIRMACIÓN
        # ====================================================
        await interaction.response.send_message(
            "✅ **¡Verificación completada!**\n\n"
            "🎉 Se te asignó el rol **Verificado**.\n"
            "🔓 Ahora podés ver los canales del servidor.\n\n"
            "📜 El rol `v` es independiente de la verificación.",
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
        # Registrar botón persistente
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
        description="Configura el sistema de verificación."
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
        # COMPROBAR BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.followup.send(
                "❌ No pude obtener la información del bot.",
                ephemeral=True
            )
            return
        if not bot_member.guild_permissions.administrator:
            await interaction.followup.send(
                "❌ El bot necesita el permiso "
                "**Administrador** para configurar "
                "el sistema.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR ROL VERIFICADO
        # ====================================================
        verified_role = get_verified_role(
            guild
        )
        if verified_role is None:
            verified_role = await guild.create_role(
                name=VERIFIED_ROLE_NAME,
                color=discord.Color.green(),
                reason="Sistema de verificación."
            )
        # ====================================================
        # CREAR CATEGORÍA
        # ====================================================
        category = discord.utils.get(
            guild.categories,
            name=VERIFICATION_CATEGORY_NAME
        )
        if category is None:
            category = await guild.create_category(
                name=VERIFICATION_CATEGORY_NAME,
                reason="Sistema de verificación."
            )
        # ====================================================
        # CREAR CANAL REGLAS
        # ====================================================
        rules_channel = discord.utils.get(
            guild.text_channels,
            name=RULES_CHANNEL_NAME
        )
        if rules_channel is None:
            rules_channel = await guild.create_text_channel(
                name=RULES_CHANNEL_NAME,
                category=category,
                reason="Sistema de verificación."
            )
        # ====================================================
        # CREAR CANAL VERIFICACIÓN
        # ====================================================
        verification_channel = discord.utils.get(
            guild.text_channels,
            name=VERIFICATION_CHANNEL_NAME
        )
        if verification_channel is None:
            verification_channel = await guild.create_text_channel(
                name=VERIFICATION_CHANNEL_NAME,
                category=category,
                reason="Sistema de verificación."
            )
        # ====================================================
        # ASEGURAR CATEGORÍA
        # ====================================================
        try:
            if rules_channel.category_id != category.id:
                await rules_channel.edit(
                    category=category
                )
            if verification_channel.category_id != category.id:
                await verification_channel.edit(
                    category=category
                )
        except discord.HTTPException:
            pass
        # ====================================================
        # CONFIGURAR PERMISOS
        # ====================================================
        await configure_verification_permissions(
            guild,
            verified_role,
            rules_channel,
            verification_channel
        )
        # ====================================================
        # GUARDAR CONFIGURACIÓN
        # ====================================================
        data = load_data()
        guild_id = str(
            guild.id
        )
        if guild_id not in data:
            data[guild_id] = {}
        data[guild_id].update({
            "verified_role_id":
                verified_role.id,
            "rules_channel_id":
                rules_channel.id,
            "verification_channel_id":
                verification_channel.id,
            "setup_completed":
                True
        })
        save_data(
            data
        )
        # ====================================================
        # PUBLICAR VERIFICACIÓN
        # ====================================================
        verification_embed = discord.Embed(
            title="✅ Verificación",
            description=(
                "Para acceder al resto del servidor, "
                "presioná el botón **Verificarme**.\n\n"
                "🔒 Los usuarios no verificados solamente "
                "pueden ver `#reglas` y `#verificacion`.\n\n"
                "🔓 Después de verificarte, recibirás el rol "
                "**Verificado** y podrás acceder a los "
                "demás canales.\n\n"
                "📜 El rol `v` se asigna desde el canal "
                "`#reglas` y es independiente de este sistema."
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
        # RESPUESTA FINAL
        # ====================================================
        await interaction.followup.send(
            "✅ **Sistema de verificación configurado correctamente.**\n\n"
            f"📜 Reglas: {rules_channel.mention}\n"
            f"✅ Verificación: "
            f"{verification_channel.mention}\n"
            f"👤 Rol de verificación: "
            f"{verified_role.mention}\n\n"
            "🔒 Sin `Verificado` → solo reglas y verificación.\n"
            "🔓 Con `Verificado` → acceso a los canales normales.\n\n"
            "ℹ️ El rol `v` no participa en la verificación.",
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