import discord
from discord import app_commands
from discord.ext import commands
class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Guarda los usuarios AFK
        #
        # Formato:
        # {
        #     user_id: "motivo"
        # }
        #
        self.afk_users = {}
    # =========================
    # COMANDO AFK
    # =========================
    @app_commands.command(
        name="afk",
        description="Activa o desactiva tu estado AFK."
    )
    @app_commands.describe(
        estado="Elegí si querés activar o desactivar tu AFK.",
        motivo="Motivo por el que estás AFK."
    )
    @app_commands.choices(
        estado=[
            app_commands.Choice(
                name="Activar AFK",
                value="on"
            ),
            app_commands.Choice(
                name="Desactivar AFK",
                value="off"
            )
        ]
    )
    async def afk(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str] = None,
        motivo: str = None
    ):
        usuario = interaction.user
        # =========================
        # DESACTIVAR AFK
        # =========================
        if estado and estado.value == "off":
            if usuario.id not in self.afk_users:
                await interaction.response.send_message(
                    f"❌ {usuario.mention}, no estás en AFK.",
                    ephemeral=True
                )
                return
            # Eliminar AFK
            del self.afk_users[
                usuario.id
            ]
            embed = discord.Embed(
                title="👋 AFK desactivado",
                description=(
                    f"Bienvenido de nuevo, "
                    f"{usuario.mention}."
                )
            )
            embed.set_thumbnail(
                url=usuario.display_avatar.url
            )
            await interaction.response.send_message(
                embed=embed
            )
            return
        # =========================
        # COMPROBAR SI YA ESTÁ AFK
        # =========================
        if usuario.id in self.afk_users:
            await interaction.response.send_message(
                f"💤 {usuario.mention}, ya estás en AFK.\n"
                f"Usá `/afk` y elegí **Desactivar AFK** "
                f"para quitarlo.",
                ephemeral=True
            )
            return
        # =========================
        # MOTIVO POR DEFECTO
        # =========================
        if not motivo:
            motivo = "Sin motivo"
        # =========================
        # GUARDAR AFK
        # =========================
        self.afk_users[
            usuario.id
        ] = motivo
        # =========================
        # EMBED
        # =========================
        embed = discord.Embed(
            title="💤 AFK activado",
            description=(
                f"{usuario.mention} ahora está AFK."
            )
        )
        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )
        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )
        embed.set_footer(
            text="Tu AFK se quitará automáticamente cuando vuelvas a hablar."
        )
        await interaction.response.send_message(
            embed=embed
        )
    # =========================
    # DETECTAR MENSAJES
    # =========================
    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):
        # Ignorar mensajes de bots
        if message.author.bot:
            return
        # =========================
        # QUITAR AFK AL HABLAR
        # =========================
        if message.author.id in self.afk_users:
            del self.afk_users[
                message.author.id
            ]
            await message.channel.send(
                f"👋 Bienvenido de nuevo, "
                f"{message.author.mention}.\n"
                f"Tu AFK fue desactivado automáticamente."
            )
        # =========================
        # AVISAR SI MENCIONAN A UN AFK
        # =========================
        for usuario in message.mentions:
            if usuario.id in self.afk_users:
                motivo = self.afk_users[
                    usuario.id
                ]
                await message.channel.send(
                    f"💤 {usuario.mention} está AFK.\n"
                    f"📝 **Motivo:** {motivo}"
                )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        AFK(bot)
    )