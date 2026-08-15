import discord
from discord.ext import commands
from discord import app_commands

from math import ceil


# ============================================================
# CONFIGURACIÓN
# ============================================================

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)

COMMANDS_PER_PAGE = 8


# ============================================================
# CATEGORÍAS
# ============================================================

CATEGORIES = {

    "🛡️・Moderación": [
        "ban",
        "kick",
        "timeout",
        "untimeout",
        "mute",
        "clear",
        "lock",
        "unlock",
    ],

    "🔐・Seguridad": [
        "antilink",
        "antiflood",
        "antispam",
        "verification",
    ],

    "💰・Economía": [
        "balance",
        "daily",
        "work",
        "pay",
        "coinflip",
        "dice",
        "slots",
        "guess",
        "leaderboard",
        "economia",
        "bet",
        "blackjack",
        "roulette",
    ],

    "💜・Acciones": [
        "hug",
        "kiss",
        "slap",
        "pat",
        "cuddle",
        "love",
        "punch",
        "bite",
        "highfive",
        "wave",
        "returnkiss",
        "returnhug",
        "actionstats",
    ],

    "🎭・Roles": [
        "addrole",
        "createrole",
        "deleterole",
        "reactionroles",
        "edad",
        "rolesdecorativos",
        "mediarol",
    ],

    "🎫・Tickets": [
        "ticket",
        "tickets",
        "closeticket",
    ],

    "👋・Servidor": [
        "setbienvenida",
        "testbienvenida",
        "reglas",
        "server",
        "setup",
        "logs",
    ],

    "🎵・Música": [
        "play",
        "pause",
        "resume",
        "skip",
        "stop",
        "queue",
        "volume",
        "leave",
    ],

    "🎮・Entretenimiento": [
        "spotify",
        "avatar",
        "dance",
        "cry",
        "happy",
        "genai",
    ],

    "👤・Usuarios": [
        "afk",
        "userinfo",
        "nick",
        "avatar",
        "status",
    ],

    "📊・Invitaciones": [
        "invite",
        "invites",
        "invitesleaderboard",
    ],

    "🔧・Utilidades": [
        "ping",
        "say",
        "conteo",
        "addemoji",
        "voice",
    ],

    "🤖・Bot": [
        "botinfo",
        "test",
        "help",
        "config",
        "key",
    ],

    "👑・Owner": [
        "owner",
        "setstatus",
        "clearstatus",
    ],
}


# ============================================================
# DESCRIPCIONES
# ============================================================

CATEGORY_DESCRIPTIONS = {

    "🛡️・Moderación":
        "Herramientas para administrar y moderar el servidor.",

    "🔐・Seguridad":
        "Sistemas automáticos para proteger tu servidor.",

    "💰・Economía":
        "Dinero, apuestas, juegos y estadísticas económicas.",

    "💜・Acciones":
        "Interactuá con otros usuarios mediante GIFs y acciones.",

    "🎭・Roles":
        "Sistemas para crear, administrar y seleccionar roles.",

    "🎫・Tickets":
        "Sistema de soporte mediante tickets privados.",

    "👋・Servidor":
        "Configuración general y sistemas automáticos del servidor.",

    "🎵・Música":
        "Comandos relacionados con reproducción de música.",

    "🎮・Entretenimiento":
        "Comandos para divertirte y generar contenido.",

    "👤・Usuarios":
        "Información y funciones relacionadas con usuarios.",

    "📊・Invitaciones":
        "Estadísticas y sistemas de invitaciones.",

    "🔧・Utilidades":
        "Herramientas generales para el servidor.",

    "🤖・Bot":
        "Información y herramientas del bot.",

    "👑・Owner":
        "Comandos exclusivos para el propietario del bot.",
}


# ============================================================
# HELP COG
# ============================================================

class Help(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "[HELP] Sistema de ayuda cargado."
        )

    # ========================================================
    # OBTENER COMANDOS
    # ========================================================

    def get_commands_for_category(
        self,
        category
    ):

        available = []

        commands_by_name = {
            command.name: command
            for command in self.bot.commands
            if not command.hidden
        }

        for name in CATEGORIES.get(
            category,
            []
        ):

            command = commands_by_name.get(
                name
            )

            if command:

                available.append(
                    command
                )

        return available

    # ========================================================
    # COMANDOS NO CLASIFICADOS
    # ========================================================

    def get_uncategorized_commands(
        self
    ):

        categorized = set()

        for commands_list in CATEGORIES.values():

            categorized.update(
                commands_list
            )

        return [
            command
            for command in self.bot.commands
            if (
                not command.hidden
                and command.name not in categorized
                and command.name != "help"
            )
        ]

    # ========================================================
    # CREAR EMBED PRINCIPAL
    # ========================================================

    def main_embed(
        self,
        ctx
    ):

        total_commands = len([
            command
            for command in self.bot.commands
            if not command.hidden
        ])

        total_categories = len(
            CATEGORIES
        )

        embed = discord.Embed(
            title="💜・CENTRO DE AYUDA",
            description=(
                f"Bienvenido al sistema de ayuda de "
                f"**{ctx.guild.name}**.\n\n"

                "Seleccioná una categoría en el menú "
                "de abajo para ver todos sus comandos.\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                f"📚 **Categorías:** `{total_categories}`\n"
                f"⚡ **Comandos:** `{total_commands}`\n"
                f"⌨️ **Prefix:** `s!`\n"
                f"⚡ **Slash:** `/`\n\n"

                "💡 **Todos los comandos compatibles funcionan "
                "con `s!` y `/`.**\n\n"

                "Ejemplo:\n"
                "`s!balance`\n"
                "`/balance`"
            ),
            color=PURPLE
        )

        if self.bot.user:

            embed.set_thumbnail(
                url=self.bot.user.display_avatar.url
            )

        embed.set_footer(
            text=(
                f"{self.bot.user.name if self.bot.user else 'Bot'} "
                "• Sistema de ayuda"
            )
        )

        return embed

    # ========================================================
    # EMBED CATEGORÍA
    # ========================================================

    def category_embed(
        self,
        category,
        commands_list,
        page=1
    ):

        total_pages = max(
            1,
            ceil(
                len(commands_list)
                / COMMANDS_PER_PAGE
            )
        )

        page = max(
            1,
            min(
                page,
                total_pages
            )
        )

        start = (
            page - 1
        ) * COMMANDS_PER_PAGE

        end = (
            start
            + COMMANDS_PER_PAGE
        )

        page_commands = commands_list[
            start:end
        ]

        description = (
            f"{CATEGORY_DESCRIPTIONS.get(category, '')}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        for command in page_commands:

            description += (
                f"**`s!{command.name}`**\n"
                f"↳ {command.description or 'Sin descripción.'}\n\n"
            )

        if not page_commands:

            description += (
                "❌ No hay comandos disponibles "
                "en esta categoría."
            )

        embed = discord.Embed(
            title=category,
            description=description,
            color=PURPLE
        )

        embed.set_footer(
            text=(
                f"Página {page}/{total_pages} "
                f"• {len(commands_list)} comandos"
            )
        )

        return embed

    # ========================================================
    # INFO EMBED
    # ========================================================

    def info_embed(
        self
    ):

        embed = discord.Embed(
            title="📖・CÓMO USAR EL BOT",
            description=(
                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "### ⌨️ Prefix\n"
                "Los comandos tradicionales utilizan:\n"
                "`s!comando`\n\n"

                "### ⚡ Slash Commands\n"
                "También podés utilizar:\n"
                "`/comando`\n\n"

                "### 👤 Mencionar usuarios\n"
                "Cuando un comando pide un usuario:\n"
                "`s!hug @usuario`\n\n"

                "### 💰 Ejemplo de economía\n"
                "`s!balance`\n"
                "`s!daily`\n"
                "`s!work`\n"
                "`s!slots 500`\n\n"

                "### 💜 Ejemplo de acciones\n"
                "`s!kiss @usuario`\n"
                "`s!hug @usuario`\n"
                "`s!actionstats`\n\n"

                "### 🎫 Soporte\n"
                "Usá el sistema de tickets del servidor "
                "para pedir ayuda.\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "💡 **Tip:** si usás `/`, Discord te mostrará "
                "automáticamente los argumentos disponibles."
            ),
            color=PURPLE
        )

        return embed

    # ========================================================
    # SEARCH EMBED
    # ========================================================

    def search_embed(
        self,
        query
    ):

        query = query.lower()

        results = []

        for command in self.bot.commands:

            if command.hidden:
                continue

            if (
                query in command.name.lower()
                or query in (
                    command.description or ""
                ).lower()
            ):

                results.append(
                    command
                )

        results = sorted(
            results,
            key=lambda command: command.name
        )

        if not results:

            description = (
                "❌ No encontré ningún comando "
                f"relacionado con `{query}`."
            )

        else:

            description = (
                f"🔎 Resultados para **`{query}`**\n\n"
            )

            for command in results[:15]:

                description += (
                    f"**`s!{command.name}`**\n"
                    f"↳ {command.description or 'Sin descripción.'}\n\n"
                )

        embed = discord.Embed(
            title="🔎・BUSCADOR",
            description=description,
            color=PURPLE
        )

        embed.set_footer(
            text=f"{len(results)} resultado(s)"
        )

        return embed

    # ========================================================
    # VIEW PRINCIPAL
    # ========================================================

    @commands.hybrid_command(
        name="help",
        description="Abre el centro de ayuda del bot."
    )
    async def help_command(
        self,
        ctx
    ):

        view = HelpView(
            self,
            ctx.author.id
        )

        await ctx.send(
            embed=self.main_embed(ctx),
            view=view
        )


# ============================================================
# SELECTOR DE CATEGORÍAS
# ============================================================

class CategorySelect(
    discord.ui.Select
):

    def __init__(
        self,
        cog,
        author_id
    ):

        self.cog = cog
        self.author_id = author_id

        options = []

        for category, commands_list in CATEGORIES.items():

            available = (
                cog.get_commands_for_category(
                    category
                )
            )

            if available:

                options.append(
                    discord.SelectOption(
                        label=category[:100],
                        description=(
                            CATEGORY_DESCRIPTIONS.get(
                                category,
                                "Ver comandos."
                            )[:100]
                        ),
                        value=category
                    )
                )

        options.append(
            discord.SelectOption(
                label="📖・Cómo usar el bot",
                description="Guía rápida para aprender a usarlo.",
                value="__info__"
            )
        )

        super().__init__(
            placeholder="📚 Elegí una categoría...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Este menú pertenece a otra persona.",
                ephemeral=True
            )

            return

        value = self.values[0]

        if value == "__info__":

            await interaction.response.edit_message(
                embed=self.cog.info_embed(),
                view=self.view
            )

            return

        commands_list = (
            self.cog.get_commands_for_category(
                value
            )
        )

        await interaction.response.edit_message(
            embed=self.cog.category_embed(
                value,
                commands_list,
                1
            ),
            view=self.view
        )


# ============================================================
# HELP VIEW
# ============================================================

class HelpView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        author_id
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.author_id = author_id

        self.current_category = None
        self.current_page = 1

        self.add_item(
            CategorySelect(
                cog,
                author_id
            )
        )

    # ========================================================
    # VERIFICAR USUARIO
    # ========================================================

    async def interaction_check(
        self,
        interaction
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Solo la persona que abrió este help "
                "puede utilizar sus botones.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # INICIO
    # ========================================================

    @discord.ui.button(
        label="Inicio",
        emoji="🏠",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def home_button(
        self,
        interaction,
        button
    ):

        self.current_category = None
        self.current_page = 1

        await interaction.response.edit_message(
            embed=self.cog.main_embed(
                await self.get_context_guild(interaction)
            ),
            view=self
        )

    # ========================================================
    # INFO
    # ========================================================

    @discord.ui.button(
        label="Guía",
        emoji="📖",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def info_button(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            embed=self.cog.info_embed(),
            view=self
        )

    # ========================================================
    # COMANDOS
    # ========================================================

    @discord.ui.button(
        label="Todos",
        emoji="📋",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def all_button(
        self,
        interaction,
        button
    ):

        commands_list = [
            command
            for command in self.cog.bot.commands
            if not command.hidden
        ]

        commands_list.sort(
            key=lambda command: command.name
        )

        embed = discord.Embed(
            title="📋・TODOS LOS COMANDOS",
            description=(
                "Estos son los comandos actualmente "
                "cargados en el bot.\n\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
            ),
            color=PURPLE
        )

        for command in commands_list:

            embed.description += (
                f"**`s!{command.name}`** "
                f"→ {command.description or 'Sin descripción.'}\n"
            )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # CERRAR
    # ========================================================

    @discord.ui.button(
        label="Cerrar",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def close_button(
        self,
        interaction,
        button
    ):

        await interaction.message.delete()

    # ========================================================
    # CONTEXTO GUILD
    # ========================================================

    async def get_context_guild(
        self,
        interaction
    ):

        class FakeContext:

            pass

        ctx = FakeContext()

        ctx.guild = interaction.guild

        return ctx


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Help(bot)
    )

    print(
        "[HELP] Sistema de ayuda activado."
    )