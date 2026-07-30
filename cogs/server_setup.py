import discord
from discord import app_commands
from discord.ext import commands


class ServerSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ============================================================
    # FUNCIONES AUXILIARES
    # ============================================================

    async def get_or_create_role(
        self,
        guild: discord.Guild,
        name: str,
        colour: discord.Colour,
        permissions: discord.Permissions | None = None
    ):
        """
        Busca un rol existente por nombre.
        Si no existe, lo crea.
        """

        role = discord.utils.get(guild.roles, name=name)

        if role:
            return role, False

        role = await guild.create_role(
            name=name,
            colour=colour,
            permissions=permissions or discord.Permissions.none(),
            reason="Configuración automática del servidor"
        )

        return role, True

    async def get_or_create_category(
        self,
        guild: discord.Guild,
        name: str
    ):
        """
        Busca una categoría existente.
        Si no existe, la crea.
        """

        category = discord.utils.get(
            guild.categories,
            name=name
        )

        if category:
            return category, False

        category = await guild.create_category(
            name=name,
            reason="Configuración automática del servidor"
        )

        return category, True

    async def get_or_create_text_channel(
        self,
        guild: discord.Guild,
        name: str,
        category: discord.CategoryChannel | None = None,
        topic: str | None = None
    ):
        """
        Busca un canal de texto existente.
        Si no existe, lo crea.
        """

        channel = discord.utils.get(
            guild.text_channels,
            name=name
        )

        if channel:
            return channel, False

        channel = await guild.create_text_channel(
            name=name,
            category=category,
            topic=topic,
            reason="Configuración automática del servidor"
        )

        return channel, True

    async def get_or_create_voice_channel(
        self,
        guild: discord.Guild,
        name: str,
        category: discord.CategoryChannel | None = None
    ):
        """
        Busca un canal de voz existente.
        Si no existe, lo crea.
        """

        channel = discord.utils.get(
            guild.voice_channels,
            name=name
        )

        if channel:
            return channel, False

        channel = await guild.create_voice_channel(
            name=name,
            category=category,
            reason="Configuración automática del servidor"
        )

        return channel, True

    # ============================================================
    # COMANDO /SERVER-SETUP
    # ============================================================

    @app_commands.command(
        name="server-setup",
        description="Configura automáticamente el servidor."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def server_setup(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        created_roles = []
        existing_roles = []

        created_categories = []
        existing_categories = []

        created_channels = []
        existing_channels = []

        # ========================================================
        # ROLES
        # ========================================================

        # Rol Staff
        staff_permissions = discord.Permissions(
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
            manage_channels=True,
            manage_roles=True,
            view_audit_log=True
        )

        staff_role, created = await self.get_or_create_role(
            guild,
            "Staff",
            discord.Colour.orange(),
            staff_permissions
        )

        if created:
            created_roles.append("Staff")
        else:
            existing_roles.append("Staff")

        # Rol Miembro
        member_role, created = await self.get_or_create_role(
            guild,
            "Miembro",
            discord.Colour.blue()
        )

        if created:
            created_roles.append("Miembro")
        else:
            existing_roles.append("Miembro")

        # Rol Bots
        bot_role, created = await self.get_or_create_role(
            guild,
            "Bots",
            discord.Colour.purple()
        )

        if created:
            created_roles.append("Bots")
        else:
            existing_roles.append("Bots")

        # ========================================================
        # CATEGORÍA INFORMACIÓN
        # ========================================================

        info_category, created = await self.get_or_create_category(
            guild,
            "📌 INFORMACIÓN"
        )

        if created:
            created_categories.append("📌 INFORMACIÓN")
        else:
            existing_categories.append("📌 INFORMACIÓN")

        # Canal bienvenida
        welcome_channel, created = await self.get_or_create_text_channel(
            guild,
            "👋・bienvenidas",
            info_category,
            "Canal de bienvenida del servidor."
        )

        if created:
            created_channels.append("👋・bienvenidas")
        else:
            existing_channels.append("👋・bienvenidas")

        # Canal reglas
        rules_channel, created = await self.get_or_create_text_channel(
            guild,
            "📜・reglas",
            info_category,
            "Reglas oficiales del servidor."
        )

        if created:
            created_channels.append("📜・reglas")
        else:
            existing_channels.append("📜・reglas")

        # Canal anuncios
        announcements_channel, created = await self.get_or_create_text_channel(
            guild,
            "📢・anuncios",
            info_category,
            "Anuncios importantes del servidor."
        )

        if created:
            created_channels.append("📢・anuncios")
        else:
            existing_channels.append("📢・anuncios")

        # ========================================================
        # CATEGORÍA COMUNIDAD
        # ========================================================

        community_category, created = await self.get_or_create_category(
            guild,
            "💬 COMUNIDAD"
        )

        if created:
            created_categories.append("💬 COMUNIDAD")
        else:
            existing_categories.append("💬 COMUNIDAD")

        # General
        general_channel, created = await self.get_or_create_text_channel(
            guild,
            "💬・general",
            community_category,
            "Canal principal de conversación."
        )

        if created:
            created_channels.append("💬・general")
        else:
            existing_channels.append("💬・general")

        # Media
        media_channel, created = await self.get_or_create_text_channel(
            guild,
            "📸・media",
            community_category,
            "Comparte imágenes, vídeos y contenido."
        )

        if created:
            created_channels.append("📸・media")
        else:
            existing_channels.append("📸・media")

        # Sugerencias
        suggestions_channel, created = await self.get_or_create_text_channel(
            guild,
            "💡・sugerencias",
            community_category,
            "Envía tus sugerencias para mejorar el servidor."
        )

        if created:
            created_channels.append("💡・sugerencias")
        else:
            existing_channels.append("💡・sugerencias")

        # ========================================================
        # CATEGORÍA BOT
        # ========================================================

        bot_category, created = await self.get_or_create_category(
            guild,
            "🤖 BOT"
        )

        if created:
            created_categories.append("🤖 BOT")
        else:
            existing_categories.append("🤖 BOT")

        # Canal comandos
        commands_channel, created = await self.get_or_create_text_channel(
            guild,
            "🤖・comandos",
            bot_category,
            "Utiliza aquí los comandos del bot."
        )

        if created:
            created_channels.append("🤖・comandos")
        else:
            existing_channels.append("🤖・comandos")

        # Canal logs
        logs_channel, created = await self.get_or_create_text_channel(
            guild,
            "📋・logs",
            bot_category,
            "Registros automáticos del servidor."
        )

        if created:
            created_channels.append("📋・logs")
        else:
            existing_channels.append("📋・logs")

        # ========================================================
        # CATEGORÍA VOZ
        # ========================================================

        voice_category, created = await self.get_or_create_category(
            guild,
            "🔊 VOZ"
        )

        if created:
            created_categories.append("🔊 VOZ")
        else:
            existing_categories.append("🔊 VOZ")

        # Canal voz general
        voice_channel, created = await self.get_or_create_voice_channel(
            guild,
            "🔊・General",
            voice_category
        )

        if created:
            created_channels.append("🔊・General")
        else:
            existing_channels.append("🔊・General")

        # Canal música
        music_channel, created = await self.get_or_create_voice_channel(
            guild,
            "🎵・Música",
            voice_category
        )

        if created:
            created_channels.append("🎵・Música")
        else:
            existing_channels.append("🎵・Música")

        # ========================================================
        # EMBED DE RESULTADO
        # ========================================================

        embed = discord.Embed(
            title="⚙️ Servidor configurado",
            description=(
                "La configuración automática terminó correctamente.\n\n"
                "Los elementos que ya existían fueron reutilizados "
                "para evitar duplicados."
            ),
            colour=discord.Colour.blurple()
        )

        embed.add_field(
            name="🛡️ Roles creados",
            value=(
                "\n".join(f"• {role}" for role in created_roles)
                if created_roles
                else "Ninguno"
            ),
            inline=False
        )

        embed.add_field(
            name="📁 Categorías creadas",
            value=(
                "\n".join(f"• {category}" for category in created_categories)
                if created_categories
                else "Ninguna"
            ),
            inline=False
        )

        embed.add_field(
            name="💬 Canales creados",
            value=(
                "\n".join(f"• {channel}" for channel in created_channels)
                if created_channels
                else "Ninguno"
            ),
            inline=False
        )

        embed.add_field(
            name="♻️ Elementos reutilizados",
            value=(
                f"Roles: `{len(existing_roles)}`\n"
                f"Categorías: `{len(existing_categories)}`\n"
                f"Canales: `{len(existing_channels)}`"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Configurado por {interaction.user}"
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

    # ============================================================
    # MANEJO DE ERRORES
    # ============================================================

    @server_setup.error
    async def server_setup_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):

        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            message = (
                "❌ No tenés permisos para usar este comando.\n"
                "Necesitás el permiso **Administrador**."
            )

        elif isinstance(
            error,
            app_commands.errors.BotMissingPermissions
        ):
            message = (
                "❌ No tengo suficientes permisos para configurar "
                "el servidor.\n"
                "Dame permisos de **Administrador** e intentá nuevamente."
            )

        else:
            print(
                f"[ERROR] server-setup: {error}"
            )

            message = (
                "❌ Ocurrió un error al configurar el servidor.\n"
                "Revisá la consola del bot para ver más información."
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


# ================================================================
# SETUP DEL COG
# ================================================================

async def setup(bot):
    await bot.add_cog(ServerSetup(bot))