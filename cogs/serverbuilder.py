import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN DE PLANTILLAS
# ============================================================
TEMPLATES = {
    "comunidad": {
        "name": "🌐 Comunidad",
        "categories": {
            "📌 INFORMACIÓN": [
                "📜・reglas",
                "📢・anuncios",
                "📖・información"
            ],
            "💬 COMUNIDAD": [
                "💬・general",
                "📸・multimedia",
                "💡・sugerencias"
            ],
            "🎫 SOPORTE": [
                "🎫・tickets"
            ],
            "🔊 VOZ": [
                "🔊・General",
                "🎵・Música"
            ]
        }
    },
    "gaming": {
        "name": "🎮 Gaming",
        "categories": {
            "📌 INFORMACIÓN": [
                "📜・reglas",
                "📢・anuncios"
            ],
            "🎮 GAMING": [
                "🎮・general",
                "🏆・competitivo",
                "📸・clips",
                "💡・sugerencias"
            ],
            "🎫 SOPORTE": [
                "🎫・tickets"
            ],
            "🔊 VOZ": [
                "🔊・Sala 1",
                "🔊・Sala 2",
                "🎮・Gaming"
            ]
        }
    },
    "completa": {
        "name": "🚀 Completa",
        "categories": {
            "📌 INFORMACIÓN": [
                "📜・reglas",
                "📢・anuncios",
                "📖・información"
            ],
            "💬 COMUNIDAD": [
                "💬・general",
                "📸・multimedia",
                "🎥・clips",
                "💡・sugerencias"
            ],
            "🎮 GAMING": [
                "🎮・gaming",
                "🏆・competitivo",
                "🎯・eventos"
            ],
            "🎫 SOPORTE": [
                "🎫・tickets",
                "📩・contacto"
            ],
            "🛡️ STAFF": [
                "🔒・staff",
                "📋・logs"
            ],
            "🔊 VOZ": [
                "🔊・General",
                "🎮・Gaming 1",
                "🎮・Gaming 2",
                "🎵・Música"
            ]
        }
    }
}
# ============================================================
# ROLES
# ============================================================
ROLES = [
    ("👑 Owner", discord.Color.gold()),
    ("🛡️ Admin", discord.Color.red()),
    ("🔨 Moderador", discord.Color.orange()),
    ("🧑‍💻 Staff", discord.Color.blue()),
    ("💎 VIP", discord.Color.purple()),
    ("👤 Miembro", discord.Color.green())
]
# ============================================================
# SELECTOR DE PLANTILLA
# ============================================================
class TemplateSelect(
    discord.ui.Select
):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Comunidad",
                description="Servidor para una comunidad general.",
                emoji="🌐",
                value="comunidad"
            ),
            discord.SelectOption(
                label="Gaming",
                description="Servidor orientado a videojuegos.",
                emoji="🎮",
                value="gaming"
            ),
            discord.SelectOption(
                label="Completa",
                description="Servidor con todas las categorías.",
                emoji="🚀",
                value="completa"
            )
        ]
        super().__init__(
            placeholder="Seleccioná una plantilla...",
            min_values=1,
            max_values=1,
            options=options
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        # Solo el administrador que abrió el menú
        # debería poder utilizarlo
        if interaction.user.id != self.view.author_id:
            await interaction.response.send_message(
                "❌ Este menú no es para vos.",
                ephemeral=True
            )
            return
        template = self.values[0]
        await interaction.response.defer(
            ephemeral=True
        )
        await create_server_structure(
            interaction.guild,
            template
        )
        await interaction.followup.send(
            f"✅ **Servidor configurado correctamente.**\n\n"
            f"📦 Plantilla utilizada: "
            f"**{TEMPLATES[template]['name']}**\n\n"
            f"🏗️ Se crearon las categorías, canales y roles.",
            ephemeral=True
        )
        self.view.stop()
# ============================================================
# VIEW
# ============================================================
class TemplateView(
    discord.ui.View
):
    def __init__(
        self,
        author_id: int
    ):
        super().__init__(
            timeout=60
        )
        self.author_id = author_id
        self.add_item(
            TemplateSelect()
        )
# ============================================================
# CREAR ESTRUCTURA
# ============================================================
async def create_server_structure(
    guild: discord.Guild,
    template_name: str
):
    template = TEMPLATES.get(
        template_name
    )
    if template is None:
        return
    # ========================================================
    # CREAR ROLES
    # ========================================================
    created_roles = {}
    for role_name, role_color in ROLES:
        role = discord.utils.get(
            guild.roles,
            name=role_name
        )
        if role is None:
            try:
                role = await guild.create_role(
                    name=role_name,
                    color=role_color,
                    reason="Server Builder"
                )
            except discord.Forbidden:
                continue
        created_roles[
            role_name
        ] = role
    # ========================================================
    # CREAR CATEGORÍAS Y CANALES
    # ========================================================
    for category_name, channels in template[
        "categories"
    ].items():
        # Buscar categoría existente
        category = discord.utils.get(
            guild.categories,
            name=category_name
        )
        # Crear categoría
        if category is None:
            try:
                category = await guild.create_category(
                    name=category_name,
                    reason="Server Builder"
                )
            except discord.Forbidden:
                continue
        # ====================================================
        # CREAR CANALES
        # ====================================================
        for channel_name in channels:
            # Comprobar si ya existe
            existing_channel = discord.utils.get(
                category.channels,
                name=channel_name
            )
            if existing_channel:
                continue
            try:
                # Canal de voz
                if (
                    category_name == "🔊 VOZ"
                ):
                    await guild.create_voice_channel(
                        name=channel_name,
                        category=category,
                        reason="Server Builder"
                    )
                # Canal de texto
                else:
                    await guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        reason="Server Builder"
                    )
            except discord.Forbidden:
                continue
# ============================================================
# COG
# ============================================================
class ServerBuilder(
    commands.Cog
):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
    # ========================================================
    # /SERVERBUILDER
    # ========================================================
    @app_commands.command(
        name="serverbuilder",
        description="Crea automáticamente la estructura de un servidor."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def serverbuilder(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="🏗️ Server Builder",
            description=(
                "Creá automáticamente la estructura "
                "de tu servidor.\n\n"
                "Seleccioná una plantilla:\n\n"
                "🌐 **Comunidad**\n"
                "Servidor para una comunidad general.\n\n"
                "🎮 **Gaming**\n"
                "Servidor orientado a videojuegos.\n\n"
                "🚀 **Completa**\n"
                "Servidor con categorías de comunidad, "
                "gaming, soporte y staff."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Server Builder • Seleccioná una plantilla"
        )
        await interaction.response.send_message(
            embed=embed,
            view=TemplateView(
                interaction.user.id
            ),
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        ServerBuilder(bot)
    )