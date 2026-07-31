import os
import json
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
OWNER_NAME = "Valentin"
DATA_DIR = "data"
REGLAS_FILE = os.path.join(
    DATA_DIR,
    "reglas.json"
)
ROL_VERIFICADO = "Verificado"
# ============================================================
# CREAR CARPETA Y ARCHIVO
# ============================================================
def ensure_data_file():
    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )
    if not os.path.exists(
        REGLAS_FILE
    ):
        with open(
            REGLAS_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {},
                file,
                indent=4,
                ensure_ascii=False
            )
# ============================================================
# CARGAR DATOS
# ============================================================
def load_rules():
    ensure_data_file()
    try:
        with open(
            REGLAS_FILE,
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
            return {}
    except (
        json.JSONDecodeError,
        OSError
    ):
        return {}
# ============================================================
# GUARDAR DATOS
# ============================================================
def save_rules(
    data
):
    ensure_data_file()
    with open(
        REGLAS_FILE,
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
# FOOTER OWNER
# ============================================================
def set_owner_footer(
    embed,
    guild_id=None
):
    if guild_id:
        embed.set_footer(
            text=(
                f"Owner: {OWNER_NAME} • "
                f"Servidor ID: {guild_id}"
            )
        )
    else:
        embed.set_footer(
            text=(
                f"Owner: {OWNER_NAME}"
            )
        )
    return embed
# ============================================================
# BOTÓN DE ACEPTAR REGLAS
# ============================================================
class ReglasView(
    discord.ui.View
):
    def __init__(
        self
    ):
        super().__init__(
            timeout=None
        )
    # ========================================================
    # BOTÓN ACEPTAR
    # ========================================================
    @discord.ui.button(
        label="Aceptar reglas",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="reglas_aceptar"
    )
    async def aceptar_reglas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        # ====================================================
        # COMPROBAR SERVIDOR
        # ====================================================
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo puede utilizarse "
                "dentro de un servidor.",
                ephemeral=True
            )
            return
        guild = interaction.guild
        usuario = interaction.user
        # ====================================================
        # BUSCAR ROL VERIFICADO
        # ====================================================
        rol = discord.utils.get(
            guild.roles,
            name=ROL_VERIFICADO
        )
        if rol is None:
            await interaction.response.send_message(
                f"❌ No existe el rol `{ROL_VERIFICADO}`.\n\n"
                f"Un administrador debe crear el rol "
                f"`{ROL_VERIFICADO}`.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR POSICIÓN DEL ROL DEL BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.response.send_message(
                "❌ No pude obtener la información del bot "
                "en este servidor.",
                ephemeral=True
            )
            return
        if rol >= bot_member.top_role:
            await interaction.response.send_message(
                "❌ No puedo asignar el rol `Verificado`.\n\n"
                "Un administrador debe colocar el rol "
                "del bot **por encima** del rol `Verificado`.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR REGISTROS
        # ====================================================
        data = load_rules()
        guild_id = str(
            guild.id
        )
        user_id = str(
            usuario.id
        )
        # ====================================================
        # CREAR ESTRUCTURA DEL SERVIDOR
        # ====================================================
        if guild_id not in data:
            data[guild_id] = {
                "usuarios": {}
            }
        if "usuarios" not in data[guild_id]:
            data[guild_id][
                "usuarios"
            ] = {}
        usuarios = data[
            guild_id
        ][
            "usuarios"
        ]
        # ====================================================
        # COMPROBAR SI YA ACEPTÓ
        # ====================================================
        if user_id in usuarios:
            if rol in usuario.roles:
                await interaction.response.send_message(
                    "✅ Ya aceptaste las reglas anteriormente.\n\n"
                    "Tu acceso al servidor ya está habilitado.",
                    ephemeral=True
                )
                return
        # ====================================================
        # ASIGNAR ROL
        # ====================================================
        try:
            if rol not in usuario.roles:
                await usuario.add_roles(
                    rol,
                    reason=(
                        "Usuario aceptó las reglas "
                        "del servidor."
                    )
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para asignarte "
                "el rol `Verificado`.\n\n"
                "Asegurate de que mi rol esté "
                "por encima de `Verificado`.",
                ephemeral=True
            )
            return
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Discord rechazó la asignación "
                "del rol.\n\n"
                "Intentá nuevamente en unos segundos.",
                ephemeral=True
            )
            return
        # ====================================================
        # FECHA ACTUAL UTC
        # ====================================================
        fecha = datetime.now(
            timezone.utc
        ).isoformat()
        # ====================================================
        # GUARDAR ACEPTACIÓN
        # ====================================================
        usuarios[user_id] = {
            "user_id":
                usuario.id,
            "username":
                str(
                    usuario
                ),
            "display_name":
                usuario.display_name,
            "fecha":
                fecha
        }
        save_rules(
            data
        )
        # ====================================================
        # EMBED DE CONFIRMACIÓN
        # ====================================================
        embed = discord.Embed(
            title=(
                "✅ Reglas aceptadas"
            ),
            description=(
                f"¡Bienvenido/a, {usuario.mention}!\n\n"
                "Aceptaste correctamente las reglas "
                "del servidor.\n\n"
                "🔓 Tu acceso al servidor "
                "ha sido habilitado."
            ),
            color=discord.Color.green()
        )
        set_owner_footer(
            embed,
            guild.id
        )
        await interaction.response.send_message(
            embed=embed,
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
        ensure_data_file()
    # ========================================================
    # /REGLAS
    # ========================================================
    @app_commands.command(
        name="reglas",
        description=(
            "Muestra las reglas del servidor."
        )
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        administrator=True
    )
    async def reglas(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild
        # ====================================================
        # EMBED PRINCIPAL
        # ====================================================
        embed = discord.Embed(
            title=(
                "📜 Reglas del servidor"
            ),
            description=(
                "Bienvenido/a al servidor.\n\n"
                "Antes de participar, leé atentamente "
                "las reglas y presioná el botón "
                "**✅ Aceptar reglas**.\n\n"
                "Al aceptar las reglas confirmás que "
                "estás de acuerdo con las normas "
                "del servidor."
            ),
            color=discord.Color.blurple()
        )
        # ====================================================
        # REGLA 1
        # ====================================================
        embed.add_field(
            name=(
                "1️⃣ Respeto"
            ),
            value=(
                "Tratamos a todos con respeto. "
                "No se permiten insultos, acoso, "
                "discriminación ni comportamientos tóxicos."
            ),
            inline=False
        )
        # ====================================================
        # REGLA 2
        # ====================================================
        embed.add_field(
            name=(
                "2️⃣ Spam"
            ),
            value=(
                "No hagas spam, flood ni envíes "
                "mensajes repetitivos de manera excesiva."
            ),
            inline=False
        )
        # ====================================================
        # REGLA 3
        # ====================================================
        embed.add_field(
            name=(
                "3️⃣ Publicidad"
            ),
            value=(
                "No está permitida la publicidad de "
                "otros servidores, bots o servicios "
                "sin autorización del staff."
            ),
            inline=False
        )
        # ====================================================
        # REGLA 4
        # ====================================================
        embed.add_field(
            name=(
                "4️⃣ Contenido"
            ),
            value=(
                "No compartas contenido ilegal, "
                "malicioso o que pueda perjudicar "
                "a otros miembros."
            ),
            inline=False
        )
        # ====================================================
        # REGLA 5
        # ====================================================
        embed.add_field(
            name=(
                "5️⃣ Uso de canales"
            ),
            value=(
                "Utilizá cada canal para el propósito "
                "correspondiente y respetá las "
                "indicaciones del staff."
            ),
            inline=False
        )
        # ====================================================
        # REGLA 6
        # ====================================================
        embed.add_field(
            name=(
                "6️⃣ Staff"
            ),
            value=(
                "Respetá las decisiones del equipo "
                "de moderación. Si tenés un problema, "
                "contactá al staff."
            ),
            inline=False
        )
        # ====================================================
        # IMPORTANTE
        # ====================================================
        embed.add_field(
            name=(
                "⚠️ Importante"
            ),
            value=(
                "El incumplimiento de las reglas puede "
                "resultar en advertencias, expulsiones "
                "o baneos dependiendo de la gravedad."
            ),
            inline=False
        )
        # ====================================================
        # FOOTER OWNER
        # ====================================================
        set_owner_footer(
            embed,
            guild.id
        )
        # ====================================================
        # ENVIAR PANEL
        # ====================================================
        await interaction.response.send_message(
            embed=embed,
            view=ReglasView()
        )
    # ========================================================
    # /REGLAS-ACEPTADAS
    # ========================================================
    @app_commands.command(
        name="reglas-aceptadas",
        description=(
            "Muestra quiénes aceptaron las reglas."
        )
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        administrator=True
    )
    async def reglas_aceptadas(
        self,
        interaction: discord.Interaction
    ):
        guild = interaction.guild
        # ====================================================
        # CARGAR DATOS
        # ====================================================
        data = load_rules()
        guild_id = str(
            guild.id
        )
        if guild_id not in data:
            await interaction.response.send_message(
                "📋 Todavía nadie aceptó las reglas.",
                ephemeral=True
            )
            return
        usuarios = data[
            guild_id
        ].get(
            "usuarios",
            {}
        )
        if not usuarios:
            await interaction.response.send_message(
                "📋 Todavía nadie aceptó las reglas.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR LISTA
        # ====================================================
        lista = []
        for user_id, informacion in usuarios.items():
            nombre = informacion.get(
                "display_name",
                informacion.get(
                    "username",
                    "Usuario desconocido"
                )
            )
            fecha = informacion.get(
                "fecha",
                "Fecha desconocida"
            )
            try:
                fecha_dt = datetime.fromisoformat(
                    fecha.replace(
                        "Z",
                        "+00:00"
                    )
                )
                fecha_formateada = discord.utils.format_dt(
                    fecha_dt,
                    style="F"
                )
            except Exception:
                fecha_formateada = fecha
            lista.append(
                f"👤 **{nombre}**\n"
                f"🆔 `{user_id}`\n"
                f"📅 {fecha_formateada}"
            )
        # ====================================================
        # CREAR EMBED
        # ====================================================
        texto = "\n\n".join(
            lista
        )
        # ====================================================
        # LÍMITE DE DISCORD
        # ====================================================
        if len(
            texto
        ) > 3900:
            embed = discord.Embed(
                title=(
                    "📋 Usuarios que aceptaron "
                    "las reglas"
                ),
                description=(
                    f"Hay **{len(usuarios)} usuarios** "
                    "registrados como personas que "
                    "aceptaron las reglas.\n\n"
                    "La lista es demasiado larga "
                    "para mostrarla completa "
                    "en un solo mensaje."
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title=(
                    "📋 Usuarios que aceptaron "
                    "las reglas"
                ),
                description=texto,
                color=discord.Color.green()
            )
            embed.set_footer(
                text=(
                    f"Owner: {OWNER_NAME} • "
                    f"Total: {len(usuarios)} usuarios"
                )
            )
        # ====================================================
        # ENVIAR RESULTADO
        # ====================================================
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot
):
    # ========================================================
    # REGISTRAR VISTA PERSISTENTE
    # ========================================================
    bot.add_view(
        ReglasView()
    )
    # ========================================================
    # CARGAR COG
    # ========================================================
    await bot.add_cog(
        Reglas(
            bot
        )
    )