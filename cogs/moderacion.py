import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from config import OWNER_ID
class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================================================
    # COMPROBAR SI ES OWNER
    # =========================================================
    def es_owner(self, interaction: discord.Interaction):
        return interaction.user.id == int(OWNER_ID)
    # =========================================================
    # CLEAR
    # =========================================================
    @app_commands.command(
        name="clear",
        description="Elimina una cantidad de mensajes del canal."
    )
    @app_commands.describe(
        cantidad="Cantidad de mensajes a eliminar (1-100)."
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        cantidad: int
    ):
        if not self.es_owner(interaction):
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        if cantidad < 1 or cantidad > 100:
            await interaction.response.send_message(
                "❌ La cantidad debe estar entre 1 y 100.",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"🗑️ Eliminando {cantidad} mensajes...",
            ephemeral=True
        )
        await interaction.channel.purge(
            limit=cantidad
        )
        mensaje = await interaction.channel.send(
            f"🗑️ {interaction.user.mention} "
            f"eliminó {cantidad} mensajes."
        )
        await mensaje.delete(
            delay=3
        )
    # =========================================================
    # KICK
    # =========================================================
    @app_commands.command(
        name="kick",
        description="Expulsa a un usuario del servidor."
    )
    @app_commands.describe(
        miembro="Usuario que querés expulsar.",
        razon="Razón de la expulsión."
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        razon: str = "Sin razón"
    ):
        es_owner = self.es_owner(interaction)
        if not es_owner:
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        guild = interaction.guild
        if miembro == interaction.user:
            await interaction.response.send_message(
                "❌ No podés expulsarte a vos mismo.",
                ephemeral=True
            )
            return
        # El Owner puede saltarse la jerarquía del rol
        if not es_owner:
            if miembro.top_role >= interaction.user.top_role:
                await interaction.response.send_message(
                    "❌ No podés expulsar a un usuario "
                    "con un rol igual o superior al tuyo.",
                    ephemeral=True
                )
                return
        # El bot siempre necesita tener un rol superior
        if guild.me and miembro.top_role >= guild.me.top_role:
            await interaction.response.send_message(
                "❌ Mi rol está por debajo del rol de ese usuario.",
                ephemeral=True
            )
            return
        try:
            await miembro.kick(
                reason=razon
            )
            await interaction.response.send_message(
                f"👢 {miembro.mention} fue expulsado.\n"
                f"📝 Razón: {razon}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para expulsar a este usuario.",
                ephemeral=True
            )
    # =========================================================
    # BAN
    # =========================================================
    @app_commands.command(
        name="ban",
        description="Banea a un usuario del servidor."
    )
    @app_commands.describe(
        miembro="Usuario que querés banear.",
        razon="Razón del baneo."
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        razon: str = "Sin razón"
    ):
        es_owner = self.es_owner(interaction)
        if not es_owner:
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        guild = interaction.guild
        if miembro == interaction.user:
            await interaction.response.send_message(
                "❌ No podés banearte a vos mismo.",
                ephemeral=True
            )
            return
        if not es_owner:
            if miembro.top_role >= interaction.user.top_role:
                await interaction.response.send_message(
                    "❌ No podés banear a un usuario "
                    "con un rol igual o superior al tuyo.",
                    ephemeral=True
                )
                return
        if guild.me and miembro.top_role >= guild.me.top_role:
            await interaction.response.send_message(
                "❌ Mi rol está por debajo del rol de ese usuario.",
                ephemeral=True
            )
            return
        try:
            await miembro.ban(
                reason=razon
            )
            await interaction.response.send_message(
                f"🔨 {miembro.mention} fue baneado.\n"
                f"📝 Razón: {razon}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para banear a este usuario.",
                ephemeral=True
            )
    # =========================================================
    # UNBAN
    # =========================================================
    @app_commands.command(
        name="unban",
        description="Desbanea a un usuario usando su ID."
    )
    @app_commands.describe(
        usuario_id="ID del usuario que querés desbanear."
    )
    async def unban(
        self,
        interaction: discord.Interaction,
        usuario_id: str
    ):
        if not self.es_owner(interaction):
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        guild = interaction.guild
        try:
            usuario_id = int(usuario_id)
            usuario = await self.bot.fetch_user(
                usuario_id
            )
            await guild.unban(
                usuario
            )
            await interaction.response.send_message(
                f"✅ {usuario} fue desbaneado."
            )
        except ValueError:
            await interaction.response.send_message(
                "❌ El ID debe contener solamente números.",
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                "❌ Ese usuario no está baneado o el ID no es válido.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para desbanear usuarios.",
                ephemeral=True
            )
    # =========================================================
    # TIMEOUT
    # =========================================================
    @app_commands.command(
        name="timeout",
        description="Aplica un timeout a un usuario."
    )
    @app_commands.describe(
        miembro="Usuario al que querés aplicar timeout.",
        minutos="Duración en minutos (1-40320).",
        razon="Razón del timeout."
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        minutos: int,
        razon: str = "Sin razón"
    ):
        es_owner = self.es_owner(interaction)
        if not es_owner:
            if not interaction.user.guild_permissions.moderate_members:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        guild = interaction.guild
        if minutos < 1 or minutos > 40320:
            await interaction.response.send_message(
                "❌ El tiempo debe ser entre 1 minuto y 28 días.",
                ephemeral=True
            )
            return
        if miembro == interaction.user:
            await interaction.response.send_message(
                "❌ No podés aplicarte timeout a vos mismo.",
                ephemeral=True
            )
            return
        if not es_owner:
            if miembro.top_role >= interaction.user.top_role:
                await interaction.response.send_message(
                    "❌ No podés aplicar timeout a un usuario "
                    "con un rol igual o superior al tuyo.",
                    ephemeral=True
                )
                return
        if guild.me and miembro.top_role >= guild.me.top_role:
            await interaction.response.send_message(
                "❌ Mi rol está por debajo del rol de ese usuario.",
                ephemeral=True
            )
            return
        try:
            await miembro.timeout(
                timedelta(
                    minutes=minutos
                ),
                reason=razon
            )
            await interaction.response.send_message(
                f"🔇 {miembro.mention} recibió timeout.\n"
                f"⏱️ Duración: {minutos} minutos\n"
                f"📝 Razón: {razon}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para aplicar timeout.",
                ephemeral=True
            )
    # =========================================================
    # UNTIMEOUT
    # =========================================================
    @app_commands.command(
        name="untimeout",
        description="Quita el timeout a un usuario."
    )
    async def untimeout(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member
    ):
        if not self.es_owner(interaction):
            if not interaction.user.guild_permissions.moderate_members:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        try:
            await miembro.timeout(
                None
            )
            await interaction.response.send_message(
                f"🔊 Se quitó el timeout a {miembro.mention}."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para quitar el timeout.",
                ephemeral=True
            )
    # =========================================================
    # LOCK
    # =========================================================
    @app_commands.command(
        name="lock",
        description="Bloquea el canal actual."
    )
    async def lock(
        self,
        interaction: discord.Interaction
    ):
        if not self.es_owner(interaction):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            send_messages=False
        )
        await interaction.response.send_message(
            "🔒 Canal bloqueado."
        )
    # =========================================================
    # UNLOCK
    # =========================================================
    @app_commands.command(
        name="unlock",
        description="Desbloquea el canal actual."
    )
    async def unlock(
        self,
        interaction: discord.Interaction
    ):
        if not self.es_owner(interaction):
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message(
                    "❌ No tenés permisos para usar este comando.",
                    ephemeral=True
                )
                return
        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            send_messages=None
        )
        await interaction.response.send_message(
            "🔓 Canal desbloqueado."
        )
    # =========================================================
    # ERRORES
    # =========================================================
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            mensaje = (
                "❌ No tenés permisos para usar este comando."
            )
        else:
            print(
                f"❌ Error de moderación: {error}"
            )
            mensaje = (
                "❌ Ocurrió un error al ejecutar este comando."
            )
        if interaction.response.is_done():
            await interaction.followup.send(
                mensaje,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                mensaje,
                ephemeral=True
            )
# =========================================================
# CARGAR COG
# =========================================================
async def setup(bot):
    await bot.add_cog(
        Moderacion(bot)
    )