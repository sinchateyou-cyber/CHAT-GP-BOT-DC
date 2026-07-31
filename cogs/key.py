import os
import json
import secrets
import string
from datetime import datetime, timedelta, timezone
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "keys.json")
# ============================================================
# DURACIONES
# ============================================================
DURACIONES = {
    "1d": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
    "permanente": None,
}
# ============================================================
# CREAR ARCHIVO AUTOMÁTICAMENTE
# ============================================================
def ensure_data_file():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(DATA_FILE):
        with open(
            DATA_FILE,
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
def load_keys():
    ensure_data_file()
    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except Exception as error:
        print(
            f"❌ Error cargando keys.json: {error}"
        )
        return {}
# ============================================================
# GUARDAR DATOS
# ============================================================
def save_keys(data):
    ensure_data_file()
    with open(
        DATA_FILE,
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
# FECHA ACTUAL
# ============================================================
def get_now():
    return datetime.now(
        timezone.utc
    )
# ============================================================
# GENERAR KEY
# ============================================================
def generate_key():
    caracteres = (
        string.ascii_uppercase
        + string.digits
    )
    partes = []
    for _ in range(4):
        parte = "".join(
            secrets.choice(
                caracteres
            )
            for _ in range(5)
        )
        partes.append(
            parte
        )
    return "KEY-" + "-".join(
        partes
    )
# ============================================================
# COG KEYS
# ============================================================
class Keys(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keys = load_keys()
        print(
            "✅ Sistema de Keys inicializado"
        )
    # ========================================================
    # GUARDAR
    # ========================================================
    def save(self):
        save_keys(
            self.keys
        )
    # ========================================================
    # COMPROBAR KEYS EXPIRADAS
    # ========================================================
    def clean_expired(self):
        current_time = get_now()
        changed = False
        for key, data in self.keys.items():
            if data.get(
                "status"
            ) != "available":
                continue
            expires_at = data.get(
                "expires_at"
            )
            if not expires_at:
                continue
            try:
                expiration = datetime.fromisoformat(
                    expires_at
                )
                if expiration <= current_time:
                    data["status"] = "expired"
                    changed = True
            except Exception:
                continue
        if changed:
            self.save()
    # ========================================================
    # /GENKEY
    # ========================================================
    @app_commands.command(
        name="genkey",
        description="Genera una nueva key."
    )
    @app_commands.describe(
        duracion="Duración de la key."
    )
    @app_commands.choices(
        duracion=[
            app_commands.Choice(
                name="1 día",
                value="1d"
            ),
            app_commands.Choice(
                name="7 días",
                value="7d"
            ),
            app_commands.Choice(
                name="30 días",
                value="30d"
            ),
            app_commands.Choice(
                name="Permanente",
                value="permanente"
            ),
        ]
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def genkey(
        self,
        interaction: discord.Interaction,
        duracion: app_commands.Choice[str]
    ):
        self.clean_expired()
        key = generate_key()
        while key in self.keys:
            key = generate_key()
        created_at = get_now()
        duration = DURACIONES[
            duracion.value
        ]
        expires_at = None
        if duration is not None:
            expires_at = (
                created_at + duration
            ).isoformat()
        self.keys[key] = {
            "status": "available",
            "duration": duracion.value,
            "created_at":
                created_at.isoformat(),
            "expires_at":
                expires_at,
            "redeemed_by":
                None,
            "redeemed_at":
                None,
            "created_by":
                interaction.user.id,
        }
        self.save()
        embed = discord.Embed(
            title="🔑 Key generada",
            description=(
                "La key fue generada "
                "correctamente."
            ),
            colour=discord.Colour.green()
        )
        embed.add_field(
            name="🔐 Key",
            value=(
                f"```{key}```"
            ),
            inline=False
        )
        embed.add_field(
            name="⏱️ Duración",
            value=duracion.name,
            inline=True
        )
        embed.add_field(
            name="📊 Estado",
            value="🟢 Disponible",
            inline=True
        )
        if expires_at:
            embed.add_field(
                name="📅 Expira",
                value=(
                    f"<t:{int(created_at.timestamp() + duration.total_seconds())}:F>"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="📅 Expira",
                value="♾️ Nunca",
                inline=False
            )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # /REDEEM
    # ========================================================
    @app_commands.command(
        name="redeem",
        description="Canjea una key."
    )
    @app_commands.describe(
        key="Ingresá la key que querés canjear."
    )
    async def redeem(
        self,
        interaction: discord.Interaction,
        key: str
    ):
        self.clean_expired()
        key = key.upper().strip()
        if key not in self.keys:
            await interaction.response.send_message(
                "❌ Esa key no existe.",
                ephemeral=True
            )
            return
        data = self.keys[key]
        status = data.get(
            "status"
        )
        if status == "redeemed":
            await interaction.response.send_message(
                "❌ Esa key ya fue utilizada.",
                ephemeral=True
            )
            return
        if status == "revoked":
            await interaction.response.send_message(
                "❌ Esa key fue revocada.",
                ephemeral=True
            )
            return
        if status == "expired":
            await interaction.response.send_message(
                "❌ Esa key está expirada.",
                ephemeral=True
            )
            return
        if status != "available":
            await interaction.response.send_message(
                "❌ Esa key no está disponible.",
                ephemeral=True
            )
            return
        data["status"] = "redeemed"
        data["redeemed_by"] = (
            interaction.user.id
        )
        data["redeemed_at"] = (
            get_now().isoformat()
        )
        self.save()
        embed = discord.Embed(
            title="✅ Key canjeada",
            description=(
                f"{interaction.user.mention}, "
                "tu key fue canjeada correctamente."
            ),
            colour=discord.Colour.green()
        )
        embed.add_field(
            name="🔑 Key",
            value=f"`{key}`",
            inline=False
        )
        embed.add_field(
            name="⏱️ Duración",
            value=data.get(
                "duration",
                "Desconocida"
            ),
            inline=True
        )
        embed.add_field(
            name="📊 Estado",
            value="🟢 Activa",
            inline=True
        )
        await interaction.response.send_message(
            embed=embed
        )
    # ========================================================
    # /KEYINFO
    # ========================================================
    @app_commands.command(
        name="keyinfo",
        description="Consulta información de una key."
    )
    @app_commands.describe(
        key="Key que querés consultar."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def keyinfo(
        self,
        interaction: discord.Interaction,
        key: str
    ):
        self.clean_expired()
        key = key.upper().strip()
        if key not in self.keys:
            await interaction.response.send_message(
                "❌ Esa key no existe.",
                ephemeral=True
            )
            return
        data = self.keys[key]
        status = data.get(
            "status",
            "unknown"
        )
        estados = {
            "available":
                "🟢 Disponible",
            "redeemed":
                "🔵 Canjeada",
            "revoked":
                "🔴 Revocada",
            "expired":
                "🟠 Expirada",
        }
        estado_texto = estados.get(
            status,
            "❓ Desconocida"
        )
        embed = discord.Embed(
            title="🔑 Información de Key",
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name="🔐 Key",
            value=f"`{key}`",
            inline=False
        )
        embed.add_field(
            name="📊 Estado",
            value=estado_texto,
            inline=True
        )
        embed.add_field(
            name="⏱️ Duración",
            value=data.get(
                "duration",
                "Desconocida"
            ),
            inline=True
        )
        if data.get(
            "redeemed_by"
        ):
            embed.add_field(
                name="👤 Canjeada por",
                value=(
                    f"<@{data['redeemed_by']}>"
                ),
                inline=False
            )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # /REVOKEKEY
    # ========================================================
    @app_commands.command(
        name="revokekey",
        description="Revoca una key."
    )
    @app_commands.describe(
        key="Key que querés revocar."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def revokekey(
        self,
        interaction: discord.Interaction,
        key: str
    ):
        key = key.upper().strip()
        if key not in self.keys:
            await interaction.response.send_message(
                "❌ Esa key no existe.",
                ephemeral=True
            )
            return
        if self.keys[key].get(
            "status"
        ) == "revoked":
            await interaction.response.send_message(
                "❌ Esa key ya está revocada.",
                ephemeral=True
            )
            return
        self.keys[key]["status"] = "revoked"
        self.save()
        await interaction.response.send_message(
            f"🔴 La key `{key}` fue revocada correctamente.",
            ephemeral=True
        )
    # ========================================================
    # /KEYS
    # ========================================================
    @app_commands.command(
        name="keys",
        description="Muestra las estadísticas del sistema de keys."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def keys_command(
        self,
        interaction: discord.Interaction
    ):
        self.clean_expired()
        total = len(
            self.keys
        )
        available = sum(
            1
            for data in self.keys.values()
            if data.get(
                "status"
            ) == "available"
        )
        redeemed = sum(
            1
            for data in self.keys.values()
            if data.get(
                "status"
            ) == "redeemed"
        )
        revoked = sum(
            1
            for data in self.keys.values()
            if data.get(
                "status"
            ) == "revoked"
        )
        expired = sum(
            1
            for data in self.keys.values()
            if data.get(
                "status"
            ) == "expired"
        )
        embed = discord.Embed(
            title="🔑 Sistema de Keys",
            colour=discord.Colour.blurple()
        )
        embed.add_field(
            name="📦 Total",
            value=f"`{total}`",
            inline=True
        )
        embed.add_field(
            name="🟢 Disponibles",
            value=f"`{available}`",
            inline=True
        )
        embed.add_field(
            name="🔵 Canjeadas",
            value=f"`{redeemed}`",
            inline=True
        )
        embed.add_field(
            name="🔴 Revocadas",
            value=f"`{revoked}`",
            inline=True
        )
        embed.add_field(
            name="🟠 Expiradas",
            value=f"`{expired}`",
            inline=True
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # ERRORES DE ADMINISTRACIÓN
    # ========================================================
    @genkey.error
    @keyinfo.error
    @revokekey.error
    @keys_command.error
    async def admin_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            message = (
                "❌ No tenés permisos para usar "
                "este comando.\n\n"
                "Necesitás tener el permiso "
                "**Administrador**."
            )
        else:
            print(
                f"❌ Error en sistema de keys: "
                f"{type(error).__name__}: "
                f"{error}"
            )
            message = (
                "❌ Ocurrió un error al "
                "ejecutar el comando."
            )
        if interaction.response.is_done():
            await interaction.followup.send(
                message,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                message,
                ephemeral=True
            )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Keys(bot)
    )
    print(
        "✅ cogs.keys cargado correctamente"
    )