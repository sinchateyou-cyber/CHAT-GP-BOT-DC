import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
RULES_FILE = "data/rules.json"
ROLE_NAME = "v"
CHANNEL_NAME = "reglas"
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
    if not os.path.exists(RULES_FILE):
        return {}
    try:
        with open(
            RULES_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)
            if isinstance(data, dict):
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
        RULES_FILE,
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
# VIEW - ACEPTAR REGLAS
# ============================================================
class RulesView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=None
        )
    @discord.ui.button(
        label="Aceptar reglas",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="aceptar_reglas_definitivo"
    )
    async def accept_rules(
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
        # BUSCAR ROL "v"
        # ====================================================
        role = discord.utils.get(
            guild.roles,
            name=ROLE_NAME
        )
        if role is None:
            await interaction.response.send_message(
                "❌ El rol `v` no existe.\n\n"
                "Un administrador debe ejecutar "
                "`/reglas setup` para configurar el sistema.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR PERMISOS DEL BOT
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
        if role >= bot_member.top_role:
            await interaction.response.send_message(
                "❌ No puedo asignar el rol `v`.\n\n"
                "Mové el rol **v** por debajo del rol más alto "
                "del bot en la configuración de roles.",
                ephemeral=True
            )
            return
        # ====================================================
        # YA TIENE EL ROL
        # ====================================================
        if role in member.roles:
            await interaction.response.send_message(
                "✅ Ya aceptaste las reglas.",
                ephemeral=True
            )
            return
        # ====================================================
        # ASIGNAR ROL
        # ====================================================
        try:
            await member.add_roles(
                role,
                reason="Aceptación de las reglas del servidor."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No pude asignarte el rol `v`.\n\n"
                "Revisá que el rol `v` esté por debajo "
                "del rol del bot.",
                ephemeral=True
            )
            return
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Discord rechazó la asignación del rol.\n"
                "Intentá nuevamente.",
                ephemeral=True
            )
            return
        # ====================================================
        # GUARDAR ACEPTACIÓN
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
                "role_id": role.id,
                "accepted_users": {}
            }
        if "accepted_users" not in data[guild_id]:
            data[guild_id]["accepted_users"] = {}
        data[guild_id]["accepted_users"][user_id] = {
            "username":
                str(member),
            "display_name":
                member.display_name,
            "timestamp":
                discord.utils.utcnow().isoformat()
        }
        data[guild_id]["role_id"] = role.id
        save_data(data)
        # ====================================================
        # RESPUESTA
        # ====================================================
        await interaction.response.send_message(
            "✅ **¡Reglas aceptadas!**\n\n"
            "🎉 Se te asignó el rol `v`.\n"
            "🔓 Ahora podés acceder a los canales del servidor.",
            ephemeral=True
        )
# ============================================================
# COG REGLAS
# ============================================================
class Reglas(
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
            RulesView()
        )
    # ========================================================
    # /reglas setup
    # ========================================================
    reglas_group = app_commands.Group(
        name="reglas",
        description="Configura el sistema de aceptación de reglas."
    )
    @reglas_group.command(
        name="setup",
        description="Configura el canal de reglas y el rol v."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        administrator=True
    )
    async def reglas_setup(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild
        # ====================================================
        # RESPUESTA INICIAL
        # ====================================================
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
                "**Administrador** para configurar este sistema.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR / BUSCAR ROL "v"
        # ====================================================
        role = discord.utils.get(
            guild.roles,
            name=ROLE_NAME
        )
        if role is None:
            role = await guild.create_role(
                name=ROLE_NAME,
                color=discord.Color.green(),
                reason="Rol para aceptar las reglas."
            )
        # ====================================================
        # CREAR / BUSCAR CANAL
        # ====================================================
        rules_channel = discord.utils.get(
            guild.text_channels,
            name=CHANNEL_NAME
        )
        if rules_channel is None:
            rules_channel = await guild.create_text_channel(
                name=CHANNEL_NAME,
                reason="Canal del sistema de reglas."
            )
        # ====================================================
        # PERMISOS DEL CANAL DE REGLAS
        # ====================================================
        # Todos pueden ver reglas
        await rules_channel.set_permissions(
            guild.default_role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        # El rol v también puede verlo
        await rules_channel.set_permissions(
            role,
            view_channel=True,
            send_messages=False,
            read_message_history=True
        )
        # ====================================================
        # GUARDAR CONFIGURACIÓN
        # ====================================================
        data = load_data()
        guild_id = str(
            guild.id
        )
        data[guild_id] = {
            "role_id":
                role.id,
            "channel_id":
                rules_channel.id,
            "setup_completed":
                True,
            "accepted_users":
                data.get(
                    guild_id,
                    {}
                ).get(
                    "accepted_users",
                    {}
                )
        }
        save_data(data)
        # ====================================================
        # EMBED DE REGLAS
        # ====================================================
        rules_embed = discord.Embed(
            title="📜 Reglas del servidor",
            description=(
                "Antes de acceder al servidor tenés que "
                "leer y aceptar las reglas.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "**1. Respeto**\n"
                "Respetá a todos los miembros del servidor.\n\n"
                "**2. No spam**\n"
                "No hagas spam, flood ni envíes mensajes repetitivos.\n\n"
                "**3. Contenido**\n"
                "No compartas contenido ilegal, malicioso o peligroso.\n\n"
                "**4. Publicidad**\n"
                "No hagas publicidad sin autorización.\n\n"
                "**5. Canales**\n"
                "Usá cada canal para el propósito correspondiente.\n\n"
                "**6. Moderación**\n"
                "Respetá las decisiones del equipo de moderación.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Al presionar **Aceptar reglas**, confirmás que "
                "leíste y aceptás cumplir estas reglas."
            ),
            color=discord.Color.blurple()
        )
        rules_embed.set_footer(
            text="Sistema de aceptación de reglas"
        )
        # ====================================================
        # ENVIAR MENSAJE
        # ====================================================
        try:
            await rules_channel.send(
                embed=rules_embed,
                view=RulesView()
            )
        except discord.HTTPException:
            pass
        # ====================================================
        # RESPUESTA FINAL
        # ====================================================
        await interaction.followup.send(
            "✅ **Sistema de reglas configurado.**\n\n"
            f"📜 Canal: {rules_channel.mention}\n"
            f"👤 Rol: {role.mention}\n\n"
            "Cuando un usuario presione **Aceptar reglas**, "
            "recibirá automáticamente el rol `v`.",
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot
):
    await bot.add_cog(
        Reglas(
            bot
        )
    )