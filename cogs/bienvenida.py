import json
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "bienvenida.json"

PURPLE = discord.Color.from_rgb(138, 43, 226)


# ============================================================
# DATOS
# ============================================================

def load_data():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")
        return {}

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {}

        return data

    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data):
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ============================================================
# COG
# ============================================================

class Bienvenida(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()

    # ========================================================
    # OBTENER CONFIGURACIÓN DEL SERVIDOR
    # ========================================================

    def get_config(self, guild_id: int):
        guild_id = str(guild_id)

        if guild_id not in self.data:
            self.data[guild_id] = {
                "enabled": False,
                "channel_id": None,
                "message": (
                    "👋 ¡Bienvenido {usuario} a **{servidor}**! "
                    "Ahora somos **{miembros}** miembros."
                )
            }
            save_data(self.data)

        return self.data[guild_id]

    # ========================================================
    # PERMISOS
    # ========================================================

    async def cog_check(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ Este comando solamente puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return False

        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar servidor** para configurar las bienvenidas.",
                ephemeral=True
            )
            return False

        return True

    # ========================================================
    # GRUPO /BIENVENIDA
    # ========================================================

    bienvenida = app_commands.Group(
        name="bienvenida",
        description="Configura el sistema de bienvenida del servidor."
    )

    # ========================================================
    # /BIENVENIDA CANAL
    # ========================================================

    @bienvenida.command(
        name="canal",
        description="Elegí el canal donde se enviarán las bienvenidas."
    )
    @app_commands.describe(
        canal="Canal donde se enviarán las bienvenidas."
    )
    async def bienvenida_canal(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        config = self.get_config(interaction.guild.id)

        config["channel_id"] = canal.id
        config["enabled"] = True

        save_data(self.data)

        embed = discord.Embed(
            title="👋 Bienvenidas configuradas",
            description=(
                f"Las nuevas personas serán recibidas en {canal.mention}.\n\n"
                "El sistema quedó **activado** automáticamente."
            ),
            color=PURPLE
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /BIENVENIDA MENSAJE
    # ========================================================

    @bienvenida.command(
        name="mensaje",
        description="Elegí el mensaje que enviará el bot al recibir a alguien."
    )
    @app_commands.describe(
        mensaje="Mensaje de bienvenida."
    )
    async def bienvenida_mensaje(
        self,
        interaction: discord.Interaction,
        mensaje: str
    ):
        config = self.get_config(interaction.guild.id)

        config["message"] = mensaje

        save_data(self.data)

        embed = discord.Embed(
            title="💬 Mensaje actualizado",
            description=(
                "El mensaje de bienvenida fue actualizado correctamente.\n\n"
                f"**Vista previa:**\n{mensaje}"
            ),
            color=PURPLE
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /BIENVENIDA ACTIVAR
    # ========================================================

    @bienvenida.command(
        name="activar",
        description="Activa el sistema de bienvenida."
    )
    async def bienvenida_activar(
        self,
        interaction: discord.Interaction
    ):
        config = self.get_config(interaction.guild.id)

        if not config.get("channel_id"):
            await interaction.response.send_message(
                "❌ Primero tenés que elegir un canal con "
                "`/bienvenida canal`.",
                ephemeral=True
            )
            return

        config["enabled"] = True
        save_data(self.data)

        await interaction.response.send_message(
            "✅ El sistema de bienvenida fue **activado**.",
            ephemeral=True
        )

    # ========================================================
    # /BIENVENIDA DESACTIVAR
    # ========================================================

    @bienvenida.command(
        name="desactivar",
        description="Desactiva el sistema de bienvenida."
    )
    async def bienvenida_desactivar(
        self,
        interaction: discord.Interaction
    ):
        config = self.get_config(interaction.guild.id)

        config["enabled"] = False
        save_data(self.data)

        await interaction.response.send_message(
            "🛑 El sistema de bienvenida fue **desactivado**.",
            ephemeral=True
        )

    # ========================================================
    # /BIENVENIDA VER
    # ========================================================

    @bienvenida.command(
        name="ver",
        description="Muestra la configuración actual de bienvenida."
    )
    async def bienvenida_ver(
        self,
        interaction: discord.Interaction
    ):
        config = self.get_config(interaction.guild.id)

        channel_id = config.get("channel_id")
        channel = None

        if channel_id:
            channel = interaction.guild.get_channel(channel_id)

        estado = "🟢 Activado" if config.get("enabled") else "🔴 Desactivado"

        canal_texto = (
            channel.mention
            if channel
            else "❌ No configurado"
        )

        mensaje = config.get("message", "No configurado")

        embed = discord.Embed(
            title="👋 Configuración de bienvenida",
            color=PURPLE
        )

        embed.add_field(
            name="Estado",
            value=estado,
            inline=False
        )

        embed.add_field(
            name="Canal",
            value=canal_texto,
            inline=False
        )

        embed.add_field(
            name="Mensaje",
            value=mensaje[:1024],
            inline=False
        )

        embed.set_footer(
            text=f"Servidor: {interaction.guild.name}"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /BIENVENIDA PRUEBA
    # ========================================================

    @bienvenida.command(
        name="prueba",
        description="Envía una prueba del mensaje de bienvenida."
    )
    async def bienvenida_prueba(
        self,
        interaction: discord.Interaction
    ):
        config = self.get_config(interaction.guild.id)

        mensaje = self.formatear_mensaje(
            config.get("message", ""),
            interaction.user,
            interaction.guild
        )

        embed = discord.Embed(
            description=mensaje,
            color=PURPLE
        )

        embed.set_author(
            name="Vista previa de bienvenida"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # FORMATEAR MENSAJE
    # ========================================================

    def formatear_mensaje(
        self,
        mensaje: str,
        member: discord.Member,
        guild: discord.Guild
    ):
        reemplazos = {
            "{usuario}": member.mention,
            "{nombre}": member.display_name,
            "{servidor}": guild.name,
            "{miembros}": str(guild.member_count or len(guild.members)),
            "{id}": str(member.id),
        }

        for variable, valor in reemplazos.items():
            mensaje = mensaje.replace(variable, valor)

        return mensaje

    # ========================================================
    # NUEVO MIEMBRO
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.guild:
            return

        config = self.get_config(member.guild.id)

        if not config.get("enabled"):
            return

        channel_id = config.get("channel_id")

        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)

        if channel is None:
            return

        mensaje = config.get("message")

        if not mensaje:
            return

        mensaje = self.formatear_mensaje(
            mensaje,
            member,
            member.guild
        )

        embed = discord.Embed(
            description=mensaje,
            color=PURPLE
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Miembro #{member.guild.member_count}"
        )

        try:
            await channel.send(
                content=None,
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    users=True,
                    roles=False,
                    everyone=False
                )
            )

        except discord.Forbidden:
            print(
                f"[BIENVENIDA] No tengo permisos para enviar "
                f"mensajes en #{channel.name} ({member.guild.name})."
            )

        except discord.HTTPException as e:
            print(
                f"[BIENVENIDA] Error enviando bienvenida: {e}"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Bienvenida(bot))