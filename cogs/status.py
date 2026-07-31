import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# ARCHIVO DE CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
STATUS_FILE = os.path.join(
    DATA_FOLDER,
    "status.json"
)
# ============================================================
# ESTADO PREDETERMINADO
# ============================================================
DEFAULT_DATA = {
    "status": "online",
    "activity_type": None,
    "activity_text": None
}
# ============================================================
# CREAR ARCHIVO SI NO EXISTE
# ============================================================
def create_status_file():
    # Crear carpeta data/
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(
            DATA_FOLDER
        )
    # Crear status.json
    if not os.path.exists(STATUS_FILE):
        with open(
            STATUS_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                DEFAULT_DATA,
                file,
                indent=4,
                ensure_ascii=False
            )
# ============================================================
# CARGAR CONFIGURACIÓN
# ============================================================
def load_status():
    create_status_file()
    try:
        with open(
            STATUS_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)
        # Completar valores faltantes
        for key, value in DEFAULT_DATA.items():
            if key not in data:
                data[key] = value
        return data
    except Exception as error:
        print(
            f"❌ Error leyendo status.json: {error}"
        )
        return DEFAULT_DATA.copy()
# ============================================================
# GUARDAR CONFIGURACIÓN
# ============================================================
def save_status(data):
    create_status_file()
    try:
        with open(
            STATUS_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )
        print(
            "💾 Estado guardado correctamente."
        )
    except Exception as error:
        print(
            f"❌ Error guardando status.json: {error}"
        )
# ============================================================
# COG STATUS
# ============================================================
class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Crear data/status.json automáticamente
        create_status_file()
    # ========================================================
    # RESTAURAR ESTADO AL CONECTAR
    # ========================================================
    @commands.Cog.listener()
    async def on_ready(self):
        # Cargar configuración
        data = load_status()
        estado_guardado = data.get(
            "status",
            "online"
        )
        tipo_actividad = data.get(
            "activity_type"
        )
        texto_actividad = data.get(
            "activity_text"
        )
        # ====================================================
        # CONVERTIR ESTADO
        # ====================================================
        estados = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        estado = estados.get(
            estado_guardado,
            discord.Status.online
        )
        # ====================================================
        # CREAR ACTIVIDAD
        # ====================================================
        actividad = None
        if tipo_actividad and texto_actividad:
            if tipo_actividad == "playing":
                actividad = discord.Game(
                    name=texto_actividad
                )
            elif tipo_actividad == "watching":
                actividad = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=texto_actividad
                )
            elif tipo_actividad == "listening":
                actividad = discord.Activity(
                    type=discord.ActivityType.listening,
                    name=texto_actividad
                )
            elif tipo_actividad == "competing":
                actividad = discord.Activity(
                    type=discord.ActivityType.competing,
                    name=texto_actividad
                )
        # ====================================================
        # APLICAR ESTADO Y ACTIVIDAD
        # ====================================================
        try:
            await self.bot.change_presence(
                status=estado,
                activity=actividad
            )
            print(
                "🔄 Presencia restaurada:"
            )
            print(
                f"   Estado: {estado_guardado}"
            )
            if tipo_actividad:
                print(
                    f"   Actividad: "
                    f"{tipo_actividad} - "
                    f"{texto_actividad}"
                )
            else:
                print(
                    "   Actividad: Ninguna"
                )
        except Exception as error:
            print(
                f"❌ Error restaurando presencia: "
                f"{error}"
            )
    # ========================================================
    # /setstatus
    # ========================================================
    @app_commands.command(
        name="setstatus",
        description="Cambia el estado del bot."
    )
    @app_commands.describe(
        estado="Seleccioná el estado del bot."
    )
    @app_commands.choices(
        estado=[
            app_commands.Choice(
                name="🟢 Online",
                value="online"
            ),
            app_commands.Choice(
                name="🟡 Ausente",
                value="idle"
            ),
            app_commands.Choice(
                name="🔴 No molestar",
                value="dnd"
            ),
            app_commands.Choice(
                name="⚫ Invisible",
                value="invisible"
            )
        ]
    )
    async def setstatus(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        # ====================================================
        # COMPROBAR PERMISOS
        # ====================================================
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        # ====================================================
        # ESTADOS
        # ====================================================
        estados = {
            "online": discord.Status.online,
            "idle": discord.Status.idle,
            "dnd": discord.Status.dnd,
            "invisible": discord.Status.invisible
        }
        nuevo_estado = estados.get(
            estado.value
        )
        if nuevo_estado is None:
            await interaction.response.send_message(
                "❌ Estado inválido.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR CONFIGURACIÓN ACTUAL
        # ====================================================
        data = load_status()
        # Guardar nuevo estado
        data["status"] = estado.value
        # ====================================================
        # GUARDAR
        # ====================================================
        save_status(
            data
        )
        # ====================================================
        # CAMBIAR ESTADO
        # ====================================================
        await self.bot.change_presence(
            status=nuevo_estado
        )
        await interaction.response.send_message(
            f"✅ Estado cambiado a **{estado.name}**.\n"
            f"💾 Se guardó en `data/status.json`.\n"
            f"🔄 Se restaurará automáticamente al reiniciar el bot."
        )
    # ========================================================
    # /setactivity
    # ========================================================
    @app_commands.command(
        name="setactivity",
        description="Cambia la actividad del bot."
    )
    @app_commands.describe(
        tipo="Seleccioná el tipo de actividad.",
        texto="Escribí el texto de la actividad."
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(
                name="🎮 Jugando",
                value="playing"
            ),
            app_commands.Choice(
                name="👀 Viendo",
                value="watching"
            ),
            app_commands.Choice(
                name="🎧 Escuchando",
                value="listening"
            ),
            app_commands.Choice(
                name="🏆 Compitiendo",
                value="competing"
            )
        ]
    )
    async def setactivity(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        texto: str
    ):
        # ====================================================
        # COMPROBAR PERMISOS
        # ====================================================
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR TEXTO
        # ====================================================
        if len(texto) > 128:
            await interaction.response.send_message(
                "❌ El texto no puede superar los 128 caracteres.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR ACTIVIDAD
        # ====================================================
        if tipo.value == "playing":
            actividad = discord.Game(
                name=texto
            )
        elif tipo.value == "watching":
            actividad = discord.Activity(
                type=discord.ActivityType.watching,
                name=texto
            )
        elif tipo.value == "listening":
            actividad = discord.Activity(
                type=discord.ActivityType.listening,
                name=texto
            )
        elif tipo.value == "competing":
            actividad = discord.Activity(
                type=discord.ActivityType.competing,
                name=texto
            )
        else:
            await interaction.response.send_message(
                "❌ Tipo de actividad inválido.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR CONFIGURACIÓN
        # ====================================================
        data = load_status()
        # Guardar actividad
        data["activity_type"] = tipo.value
        data["activity_text"] = texto
        # ====================================================
        # GUARDAR
        # ====================================================
        save_status(
            data
        )
        # ====================================================
        # CAMBIAR ACTIVIDAD
        # ====================================================
        await self.bot.change_presence(
            activity=actividad
        )
        await interaction.response.send_message(
            f"✅ Actividad cambiada.\n"
            f"**Tipo:** {tipo.name}\n"
            f"**Texto:** `{texto}`\n\n"
            f"💾 Guardada en `data/status.json`."
        )
    # ========================================================
    # /clearactivity
    # ========================================================
    @app_commands.command(
        name="clearactivity",
        description="Elimina la actividad del bot."
    )
    async def clearactivity(
        self,
        interaction: discord.Interaction
    ):
        # ====================================================
        # COMPROBAR PERMISOS
        # ====================================================
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR CONFIGURACIÓN
        # ====================================================
        data = load_status()
        # Eliminar actividad
        data["activity_type"] = None
        data["activity_text"] = None
        # ====================================================
        # GUARDAR
        # ====================================================
        save_status(
            data
        )
        # ====================================================
        # QUITAR ACTIVIDAD
        # ====================================================
        await self.bot.change_presence(
            activity=None
        )
        await interaction.response.send_message(
            "✅ Actividad eliminada.\n"
            "💾 El cambio fue guardado."
        )
    # ========================================================
    # /clearstatus
    # ========================================================
    @app_commands.command(
        name="clearstatus",
        description="Restablece el estado del bot a Online."
    )
    async def clearstatus(
        self,
        interaction: discord.Interaction
    ):
        # ====================================================
        # COMPROBAR PERMISOS
        # ====================================================
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR CONFIGURACIÓN
        # ====================================================
        data = load_status()
        # Restablecer estado
        data["status"] = "online"
        # ====================================================
        # GUARDAR
        # ====================================================
        save_status(
            data
        )
        # ====================================================
        # CAMBIAR ESTADO
        # ====================================================
        await self.bot.change_presence(
            status=discord.Status.online
        )
        await interaction.response.send_message(
            "✅ El bot volvió a estar 🟢 **Online**.\n"
            "💾 El estado fue guardado."
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Status(bot)
    )