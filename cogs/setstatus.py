import discord
from discord import app_commands
from discord.ext import commands
class SetStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Guardar el estado actual
        self.current_type = "Jugando"
        self.current_text = "/help 💎"
    # =========================================================
    # /SETSTATUS
    # =========================================================
    @app_commands.command(
        name="setstatus",
        description="Cambia el estado y la actividad del bot."
    )
    @app_commands.describe(
        tipo="Tipo de actividad del bot.",
        texto="Texto que aparecerá en el estado."
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(
                name="🎮 Jugando",
                value="playing"
            ),
            app_commands.Choice(
                name="🎧 Escuchando",
                value="listening"
            ),
            app_commands.Choice(
                name="👀 Viendo",
                value="watching"
            ),
            app_commands.Choice(
                name="🔴 Transmitiendo",
                value="streaming"
            )
        ]
    )
    async def setstatus(
        self,
        interaction: discord.Interaction,
        tipo: app_commands.Choice[str],
        texto: str
    ):
        # =====================================================
        # CREAR ACTIVIDAD
        # =====================================================
        if tipo.value == "playing":
            activity = discord.Game(
                name=texto
            )
            display_type = "🎮 Jugando"
        elif tipo.value == "listening":
            activity = discord.Activity(
                type=discord.ActivityType.listening,
                name=texto
            )
            display_type = "🎧 Escuchando"
        elif tipo.value == "watching":
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=texto
            )
            display_type = "👀 Viendo"
        elif tipo.value == "streaming":
            activity = discord.Streaming(
                name=texto,
                url="https://twitch.tv/"
            )
            display_type = "🔴 Transmitiendo"
        else:
            return await interaction.response.send_message(
                "❌ Tipo de estado no válido.",
                ephemeral=True
            )
        # =====================================================
        # CAMBIAR ESTADO
        # =====================================================
        await self.bot.change_presence(
            activity=activity
        )
        # Guardar información
        self.current_type = display_type
        self.current_text = texto
        # =====================================================
        # CREAR EMBED
        # =====================================================
        embed = discord.Embed(
            title="✨ Estado actualizado",
            description=(
                "El estado de mi actividad fue actualizado "
                "correctamente."
            ),
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )
        # Foto actual del bot
        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )
        # Tipo
        embed.add_field(
            name="📌 Tipo",
            value=display_type,
            inline=True
        )
        # Texto
        embed.add_field(
            name="💬 Actividad",
            value=f"`{texto}`",
            inline=True
        )
        # Estado
        embed.add_field(
            name="🟢 Estado",
            value="Online",
            inline=True
        )
        # Footer
        embed.set_footer(
            text=(
                f"{self.bot.user.name} • "
                "Estado actualizado"
            ),
            icon_url=self.bot.user.display_avatar.url
        )
        await interaction.response.send_message(
            embed=embed
        )
# =============================================================
# CARGAR COG
# =============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        SetStatus(bot)
    )