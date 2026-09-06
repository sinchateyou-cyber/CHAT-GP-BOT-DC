import asyncio
import discord
from discord.ext import commands
from discord import app_commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
# Poné acá tu ID de usuario de Discord.
# Solo este usuario podrá utilizar /clonar.
OWNER_ID = 123456789012345678
# Cantidad de elementos que se procesan antes de una pequeña pausa.
# Esto ayuda a evitar golpear los rate limits de Discord.
BATCH_SIZE = 5
# ============================================================
# VISTA PARA SELECCIONAR SERVIDOR ORIGEN
# ============================================================
class SourceGuildSelect(discord.ui.Select):
    def __init__(self, author: discord.Member, bot: commands.Bot):
        self.author = author
        self.bot = bot
        guilds = sorted(bot.guilds, key=lambda g: g.name.lower())
        options = []
        for guild in guilds[:25]:
            options.append(
                discord.SelectOption(
                    label=guild.name[:100],
                    value=str(guild.id),
                    description=f"ID: {guild.id}",
                    emoji="📤"
                )
            )
        if not options:
            options.append(
                discord.SelectOption(
                    label="No hay servidores disponibles",
                    value="0"
                )
            )
        super().__init__(
            placeholder="📤 Seleccioná el servidor ORIGEN",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Este panel no es para vos.",
                ephemeral=True
            )
            return
        guild_id = int(self.values[0])
        source = self.bot.get_guild(guild_id)
        if source is None:
            await interaction.response.send_message(
                "❌ No pude encontrar el servidor.",
                ephemeral=True
            )
            return
        view = DestinationGuildView(
            author=self.author,
            bot=self.bot,
            source=source
        )
        embed = discord.Embed(
            title="📥 Seleccionar destino",
            description=(
                f"Servidor origen:\n"
                f"**{source.name}**\n\n"
                "Ahora seleccioná el servidor donde querés "
                "crear la copia."
            ),
            color=discord.Color.blurple()
        )
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )
# ============================================================
# VISTA ORIGEN
# ============================================================
class SourceGuildView(discord.ui.View):
    def __init__(self, author: discord.Member, bot: commands.Bot):
        super().__init__(timeout=120)
        self.add_item(
            SourceGuildSelect(
                author=author,
                bot=bot
            )
        )
# ============================================================
# SELECTOR DE DESTINO
# ============================================================
class DestinationGuildSelect(discord.ui.Select):
    def __init__(
        self,
        author: discord.Member,
        bot: commands.Bot,
        source: discord.Guild
    ):
        self.author = author
        self.bot = bot
        self.source = source
        guilds = sorted(
            [
                g for g in bot.guilds
                if g.id != source.id
            ],
            key=lambda g: g.name.lower()
        )
        options = []
        for guild in guilds[:25]:
            options.append(
                discord.SelectOption(
                    label=guild.name[:100],
                    value=str(guild.id),
                    description=f"ID: {guild.id}",
                    emoji="📥"
                )
            )
        if not options:
            options.append(
                discord.SelectOption(
                    label="No hay otro servidor disponible",
                    value="0"
                )
            )
        super().__init__(
            placeholder="📥 Seleccioná el servidor DESTINO",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Este panel no es para vos.",
                ephemeral=True
            )
            return
        destination_id = int(self.values[0])
        destination = self.bot.get_guild(destination_id)
        if destination is None:
            await interaction.response.send_message(
                "❌ No pude encontrar el servidor destino.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Verificar permisos
        # ----------------------------------------------------
        me = destination.me
        if me is None:
            await interaction.response.send_message(
                "❌ No pude obtener mis permisos en el servidor destino.",
                ephemeral=True
            )
            return
        if not me.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "❌ Necesito el permiso **Gestionar canales** "
                "en el servidor destino.",
                ephemeral=True
            )
            return
        if not me.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ Necesito el permiso **Gestionar roles** "
                "en el servidor destino.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Confirmación
        # ----------------------------------------------------
        embed = discord.Embed(
            title="⚠️ Confirmar clonación",
            description=(
                f"**Origen:**\n"
                f"📤 {self.source.name}\n\n"
                f"**Destino:**\n"
                f"📥 {destination.name}\n\n"
                "La clonación creará roles, categorías, canales "
                "y permisos en el servidor destino.\n\n"
                "⚠️ **No se copian mensajes ni miembros.**\n\n"
                "¿Querés continuar?"
            ),
            color=discord.Color.orange()
        )
        view = ConfirmCloneView(
            author=self.author,
            source=self.source,
            destination=destination
        )
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )
# ============================================================
# VISTA DESTINO
# ============================================================
class DestinationGuildView(discord.ui.View):
    def __init__(
        self,
        author: discord.Member,
        bot: commands.Bot,
        source: discord.Guild
    ):
        super().__init__(timeout=120)
        self.add_item(
            DestinationGuildSelect(
                author=author,
                bot=bot,
                source=source
            )
        )
# ============================================================
# CONFIRMACIÓN
# ============================================================
class ConfirmCloneView(discord.ui.View):
    def __init__(
        self,
        author: discord.Member,
        source: discord.Guild,
        destination: discord.Guild
    ):
        super().__init__(timeout=60)
        self.author = author
        self.source = source
        self.destination = destination
    @discord.ui.button(
        label="Confirmar clonación",
        style=discord.ButtonStyle.danger,
        emoji="🚀"
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Este panel no es para vos.",
                ephemeral=True
            )
            return
        await interaction.response.defer()
        # Desactivar botones
        for child in self.children:
            child.disabled = True
        try:
            await clone_guild(
                interaction,
                self.source,
                self.destination
            )
        except Exception as e:
            try:
                await interaction.followup.send(
                    "❌ Ocurrió un error durante la clonación:\n"
                    f"```{str(e)[:1800]}```",
                    ephemeral=True
                )
            except Exception:
                pass
    @discord.ui.button(
        label="Cancelar",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                "❌ Este panel no es para vos.",
                ephemeral=True
            )
            return
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="❌ Clonación cancelada",
                description="La operación fue cancelada.",
                color=discord.Color.red()
            ),
            view=None
        )
# ============================================================
# FUNCIÓN PRINCIPAL DE CLONACIÓN
# ============================================================
async def clone_guild(
    interaction: discord.Interaction,
    source: discord.Guild,
    destination: discord.Guild
):
    # --------------------------------------------------------
    # Mensaje inicial
    # --------------------------------------------------------
    embed = discord.Embed(
        title="🔄 Clonando servidor...",
        description=(
            f"📤 **Origen:** {source.name}\n"
            f"📥 **Destino:** {destination.name}\n\n"
            "Preparando clonación..."
        ),
        color=discord.Color.blurple()
    )
    message = await interaction.followup.send(
        embed=embed,
        wait=True
    )
    # --------------------------------------------------------
    # Diccionarios para relacionar IDs
    # --------------------------------------------------------
    role_map = {}
    category_map = {}
    created_roles = 0
    created_categories = 0
    created_channels = 0
    failed_channels = 0
    # ========================================================
    # 1. ROLES
    # ========================================================
    embed.description = (
        f"📤 **Origen:** {source.name}\n"
        f"📥 **Destino:** {destination.name}\n\n"
        "🛡️ Copiando roles..."
    )
    await message.edit(embed=embed)
    source_roles = [
        role for role in source.roles
        if role != source.default_role
        and not role.managed
    ]
    # Discord crea roles al final.
    # Los hacemos en orden de menor a mayor posición.
    source_roles = sorted(
        source_roles,
        key=lambda role: role.position
    )
    for index, role in enumerate(source_roles):
        try:
            new_role = await destination.create_role(
                name=role.name,
                permissions=role.permissions,
                colour=role.colour,
                hoist=role.hoist,
                mentionable=role.mentionable,
                reason=f"Clonación desde {source.name}"
            )
            role_map[role.id] = new_role
            created_roles += 1
            if index % BATCH_SIZE == 0:
                await asyncio.sleep(0.5)
        except discord.HTTPException:
            continue
    # --------------------------------------------------------
    # Intentar ordenar roles
    # --------------------------------------------------------
    try:
        positions = []
        for role in source_roles:
            new_role = role_map.get(role.id)
            if new_role:
                positions.append(
                    {
                        "id": new_role.id,
                        "position": role.position
                    }
                )
        if positions:
            await destination.edit_role_positions(
                positions=positions
            )
    except Exception:
        pass
    # ========================================================
    # 2. CATEGORÍAS
    # ========================================================
    embed.description = (
        f"📤 **Origen:** {source.name}\n"
        f"📥 **Destino:** {destination.name}\n\n"
        "📁 Copiando categorías..."
    )
    await message.edit(embed=embed)
    categories = sorted(
        source.categories,
        key=lambda category: category.position
    )
    for category in categories:
        try:
            overwrites = convert_overwrites(
                category.overwrites,
                role_map,
                destination
            )
            new_category = await destination.create_category(
                name=category.name,
                overwrites=overwrites,
                reason=f"Clonación desde {source.name}"
            )
            category_map[category.id] = new_category
            created_categories += 1
            await asyncio.sleep(0.5)
        except discord.HTTPException:
            continue
    # ========================================================
    # 3. CANALES
    # ========================================================
    embed.description = (
        f"📤 **Origen:** {source.name}\n"
        f"📥 **Destino:** {destination.name}\n\n"
        "💬 Copiando canales..."
    )
    await message.edit(embed=embed)
    channels = sorted(
        source.channels,
        key=lambda channel: (
            channel.category.position
            if channel.category
            else -1,
            channel.position
        )
    )
    for channel in channels:
        try:
            # No copiar categorías porque ya fueron creadas.
            if isinstance(channel, discord.CategoryChannel):
                continue
            overwrites = convert_overwrites(
                channel.overwrites,
                role_map,
                destination
            )
            category = None
            if channel.category:
                category = category_map.get(
                    channel.category.id
                )
            # ------------------------------------------------
            # Canal de texto
            # ------------------------------------------------
            if isinstance(channel, discord.TextChannel):
                new_channel = await destination.create_text_channel(
                    name=channel.name,
                    category=category,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    overwrites=overwrites,
                    reason=f"Clonación desde {source.name}"
                )
            # ------------------------------------------------
            # Canal de voz
            # ------------------------------------------------
            elif isinstance(channel, discord.VoiceChannel):
                new_channel = await destination.create_voice_channel(
                    name=channel.name,
                    category=category,
                    bitrate=channel.bitrate,
                    user_limit=channel.user_limit,
                    rtc_region=channel.rtc_region,
                    video_quality_mode=channel.video_quality_mode,
                    overwrites=overwrites,
                    reason=f"Clonación desde {source.name}"
                )
            # ------------------------------------------------
            # Stage
            # ------------------------------------------------
            elif isinstance(channel, discord.StageChannel):
                new_channel = await destination.create_stage_channel(
                    name=channel.name,
                    category=category,
                    overwrites=overwrites,
                    reason=f"Clonación desde {source.name}"
                )
            # ------------------------------------------------
            # Forum
            # ------------------------------------------------
            elif isinstance(channel, discord.ForumChannel):
                new_channel = await destination.create_forum(
                    name=channel.name,
                    category=category,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    overwrites=overwrites,
                    reason=f"Clonación desde {source.name}"
                )
            else:
                continue
            created_channels += 1
            await asyncio.sleep(0.7)
        except Exception:
            failed_channels += 1
            continue
    # ========================================================
    # 4. COPIAR ICONO DEL SERVIDOR
    # ========================================================
    try:
        if source.icon:
            icon_bytes = await source.icon.read()
            await destination.edit(
                icon=icon_bytes,
                reason=f"Clonación desde {source.name}"
            )
    except Exception:
        pass
    # ========================================================
    # 5. CAMBIAR NOMBRE
    # ========================================================
    try:
        await destination.edit(
            name=source.name,
            reason=f"Clonación desde {source.name}"
        )
    except Exception:
        pass
    # ========================================================
    # 6. RESULTADO
    # ========================================================
    final_embed = discord.Embed(
        title="✅ Servidor clonado",
        description=(
            f"Se terminó la clonación de **{source.name}** "
            f"a **{destination.name}**."
        ),
        color=discord.Color.green()
    )
    final_embed.add_field(
        name="🛡️ Roles",
        value=str(created_roles),
        inline=True
    )
    final_embed.add_field(
        name="📁 Categorías",
        value=str(created_categories),
        inline=True
    )
    final_embed.add_field(
        name="💬 Canales",
        value=str(created_channels),
        inline=True
    )
    final_embed.add_field(
        name="⚠️ Canales con error",
        value=str(failed_channels),
        inline=True
    )
    final_embed.add_field(
        name="🚫 No copiado",
        value=(
            "Mensajes\n"
            "Miembros\n"
            "Propietario\n"
            "Tokens\n"
            "Configuraciones internas de Discord"
        ),
        inline=False
    )
    await message.edit(
        embed=final_embed,
        view=None
    )
# ============================================================
# CONVERTIR PERMISOS
# ============================================================
def convert_overwrites(
    overwrites,
    role_map,
    destination
):
    new_overwrites = {}
    for target, overwrite in overwrites.items():
        # ----------------------------------------------------
        # @everyone
        # ----------------------------------------------------
        if isinstance(target, discord.Role):
            if target.is_default():
                new_target = destination.default_role
            else:
                new_target = role_map.get(target.id)
                if new_target is None:
                    continue
            new_overwrites[new_target] = overwrite
        # ----------------------------------------------------
        # Miembros
        # ----------------------------------------------------
        elif isinstance(target, discord.Member):
            # No copiamos permisos individuales de usuarios,
            # porque los usuarios pueden no existir en el destino.
            continue
    return new_overwrites
# ============================================================
# COG
# ============================================================
class Clonador(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(
        name="clonar",
        description="Clona la estructura de un servidor a otro."
    )
    async def clonar(
        self,
        interaction: discord.Interaction
    ):
        # ----------------------------------------------------
        # Solo dueño del bot
        # ----------------------------------------------------
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ No tenés permiso para utilizar este comando.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Verificar cantidad de servidores
        # ----------------------------------------------------
        if len(self.bot.guilds) < 2:
            await interaction.response.send_message(
                "❌ El bot debe estar en al menos **2 servidores** "
                "para poder clonar uno hacia otro.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Mostrar selector
        # ----------------------------------------------------
        embed = discord.Embed(
            title="📋 Clonador de servidores",
            description=(
                "Seleccioná el servidor que querés copiar.\n\n"
                "📤 **Servidor origen**\n"
                "Es el servidor cuya estructura se va a copiar."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Paso 1 de 2 • Seleccionar origen"
        )
        view = SourceGuildView(
            author=interaction.user,
            bot=self.bot
        )
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(
        Clonador(bot)
    )