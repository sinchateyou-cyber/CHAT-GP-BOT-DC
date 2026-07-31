import os
import json
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_DIR = "data"
REGLAS_FILE = os.path.join(DATA_DIR, "reglas.json")
ROL_VERIFICADO = "Verificado"
# ============================================================
# FUNCIONES PARA GUARDAR Y CARGAR DATOS
# ============================================================
def crear_archivo():
    """Crea la carpeta data y el archivo reglas.json si no existen."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(REGLAS_FILE):
        with open(REGLAS_FILE, "w", encoding="utf-8") as archivo:
            json.dump({}, archivo, indent=4, ensure_ascii=False)
def cargar_reglas():
    """Carga los datos guardados de reglas.json."""
    crear_archivo()
    try:
        with open(REGLAS_FILE, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if isinstance(datos, dict):
                return datos
            return {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}
def guardar_reglas(datos):
    """Guarda los datos en reglas.json."""
    crear_archivo()
    with open(REGLAS_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            datos,
            archivo,
            indent=4,
            ensure_ascii=False
        )
# ============================================================
# BOTÓN ACEPTAR REGLAS
# ============================================================
class ReglasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
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
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo puede utilizarse dentro de un servidor.",
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
                f"Creá el rol `{ROL_VERIFICADO}` y asegurate de que "
                f"el rol del bot esté por encima de él.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR DATOS
        # ====================================================
        datos = cargar_reglas()
        guild_id = str(guild.id)
        user_id = str(usuario.id)
        # Crear estructura del servidor
        if guild_id not in datos:
            datos[guild_id] = {
                "usuarios": {}
            }
        if "usuarios" not in datos[guild_id]:
            datos[guild_id]["usuarios"] = {}
        # ====================================================
        # COMPROBAR SI YA ACEPTÓ
        # ====================================================
        if user_id in datos[guild_id]["usuarios"]:
            # Si tiene el rol, informar que ya aceptó
            if rol in usuario.roles:
                await interaction.response.send_message(
                    "✅ Ya aceptaste las reglas anteriormente.",
                    ephemeral=True
                )
                return
        # ====================================================
        # DAR ROL
        # ====================================================
        try:
            if rol not in usuario.roles:
                await usuario.add_roles(
                    rol,
                    reason="El usuario aceptó las reglas del servidor."
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo asignarte el rol `Verificado`.\n\n"
                "Un administrador debe colocar el rol del bot "
                "por encima del rol `Verificado`.",
                ephemeral=True
            )
            return
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Ocurrió un error al intentar asignarte el rol.",
                ephemeral=True
            )
            return
        # ====================================================
        # GUARDAR ACEPTACIÓN
        # ====================================================
        fecha = datetime.now(timezone.utc).isoformat()
        datos[guild_id]["usuarios"][user_id] = {
            "user_id": usuario.id,
            "username": str(usuario),
            "display_name": usuario.display_name,
            "fecha": fecha
        }
        guardar_reglas(datos)
        # ====================================================
        # RESPUESTA
        # ====================================================
        await interaction.response.send_message(
            "✅ **¡Reglas aceptadas correctamente!**\n\n"
            "Ya tenés acceso al servidor.",
            ephemeral=True
        )
# ============================================================
# COG
# ============================================================
class Reglas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Crear automáticamente data/reglas.json
        crear_archivo()
    # ========================================================
    # /REGLAS
    # ========================================================
    @app_commands.command(
        name="reglas",
        description="Muestra las reglas del servidor."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reglas(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="📜 Reglas del servidor",
            description=(
                "Bienvenido/a al servidor.\n\n"
                "Antes de participar, leé atentamente las reglas "
                "y presioná el botón **✅ Aceptar reglas**.\n\n"
                "Al aceptar, confirmás que estás de acuerdo con "
                "las normas del servidor."
            ),
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="1️⃣ Respeto",
            value=(
                "Tratamos a todos con respeto. "
                "No se permiten insultos, acoso, discriminación "
                "ni comportamientos tóxicos."
            ),
            inline=False
        )
        embed.add_field(
            name="2️⃣ Spam",
            value=(
                "No hagas spam, flood ni envíes mensajes repetitivos "
                "de manera excesiva."
            ),
            inline=False
        )
        embed.add_field(
            name="3️⃣ Publicidad",
            value=(
                "No está permitida la publicidad de otros servidores, "
                "bots o servicios sin autorización del staff."
            ),
            inline=False
        )
        embed.add_field(
            name="4️⃣ Contenido",
            value=(
                "No compartas contenido ilegal, malicioso o que pueda "
                "perjudicar a otros miembros."
            ),
            inline=False
        )
        embed.add_field(
            name="5️⃣ Uso de canales",
            value=(
                "Utilizá cada canal para el propósito correspondiente "
                "y respetá las indicaciones del staff."
            ),
            inline=False
        )
        embed.add_field(
            name="6️⃣ Staff",
            value=(
                "Respetá las decisiones del equipo de moderación. "
                "Si tenés un problema, contactá al staff."
            ),
            inline=False
        )
        embed.add_field(
            name="⚠️ Importante",
            value=(
                "El incumplimiento de las reglas puede resultar en "
                "advertencias, expulsiones o baneos dependiendo "
                "de la gravedad."
            ),
            inline=False
        )
        embed.set_footer(
            text="Al aceptar las reglas recibirás el rol Verificado."
        )
        await interaction.response.send_message(
            embed=embed,
            view=ReglasView()
        )
    # ========================================================
    # /REGLAS-ACEPTADAS
    # ========================================================
    @app_commands.command(
        name="reglas-aceptadas",
        description="Muestra quiénes aceptaron las reglas."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reglas_aceptadas(
        self,
        interaction: discord.Interaction
    ):
        datos = cargar_reglas()
        guild_id = str(interaction.guild.id)
        if guild_id not in datos:
            await interaction.response.send_message(
                "📋 Todavía nadie aceptó las reglas.",
                ephemeral=True
            )
            return
        usuarios = datos[guild_id].get(
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
                    fecha.replace("Z", "+00:00")
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
        # DISCORD TIENE UN LÍMITE DE 4096 CARACTERES
        # ====================================================
        texto = "\n\n".join(lista)
        # Si hay demasiados usuarios, mostrar un resumen
        if len(texto) > 3900:
            embed = discord.Embed(
                title="📋 Reglas aceptadas",
                description=(
                    f"Hay **{len(usuarios)} usuarios** registrados "
                    "como personas que aceptaron las reglas.\n\n"
                    "La lista es demasiado larga para mostrarla "
                    "completa en un solo mensaje."
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="📋 Usuarios que aceptaron las reglas",
                description=texto,
                color=discord.Color.green()
            )
            embed.set_footer(
                text=f"Total: {len(usuarios)} usuarios"
            )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # MANEJAR ERROR DE PERMISOS
    # ========================================================
    @reglas.error
    async def reglas_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(
            error,
            app_commands.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** "
                "para utilizar este comando.",
                ephemeral=True
            )
    @reglas_aceptadas.error
    async def reglas_aceptadas_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(
            error,
            app_commands.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador** "
                "para utilizar este comando.",
                ephemeral=True
            )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    # Registrar la vista persistente
    bot.add_view(ReglasView())
    # Cargar el Cog
    await bot.add_cog(Reglas(bot))

Resultado

Cuando el bot arranque, creará automáticamente:

data/
└── reglas.json

El archivo tendrá una estructura similar a:

{
    "123456789012345678": {
        "usuarios": {
            "987654321098765432": {
                "user_id": 987654321098765432,
                "username": "Usuario#1234",
                "display_name": "Usuario",
                "fecha": "2026-07-31T10:30:00+00:00"
            }
        }
    }
}

Los comandos serán:

* /reglas → Envía el panel de reglas.
* ✅ Aceptar reglas → Guarda automáticamente al usuario en data/reglas.json y le asigna Verificado.
* /reglas-aceptadas → Muestra a los administradores quiénes aceptaron las reglas.

Importante: agregá cogs.reglas a la lista de extensiones que carga tu bot.py. El bot necesita tener el permiso Gestionar roles y su rol debe estar por encima de Verificado.