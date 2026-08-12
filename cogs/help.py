import discord
from discord.ext import commands


# ============================================================
# SELECTOR DE AYUDA
# ============================================================

class HelpSelect(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Moderación",
                emoji="🛡️",
                description="Comandos de administración"
            ),

            discord.SelectOption(
                label="Utilidades",
                emoji="⚙️",
                description="Comandos útiles"
            ),

            discord.SelectOption(
                label="Roles",
                emoji="🎭",
                description="Sistema de roles"
            ),

            discord.SelectOption(
                label="Servidor",
                emoji="🌐",
                description="Configuración del servidor"
            ),
        ]

        super().__init__(
            placeholder="💜 Seleccioná una categoría...",
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        categoria = self.values[0]

        # ====================================================
        # MODERACIÓN
        # ====================================================

        if categoria == "Moderación":

            texto = """
⬛ **Moderación**

`/ban` • `s!ban`
> Banear usuarios

`/kick` • `s!kick`
> Expulsar usuarios

`/timeout` • `s!timeout`
> Silenciar usuarios

`/clear` • `s!clear`
> Limpiar mensajes

`/lock` • `s!lock`
> Bloquear canales
"""

        # ====================================================
        # UTILIDADES
        # ====================================================

        elif categoria == "Utilidades":

            texto = """
⬛ **Utilidades**

`/avatar` • `s!avatar`
> Ver avatar

`/userinfo` • `s!userinfo`
> Información del usuario

`/botinfo` • `s!botinfo`
> Información del bot

`/ping` • `s!ping`
> Ver latencia

`/afk` • `s!afk`
> Ponerte en AFK
"""

        # ====================================================
        # ROLES
        # ====================================================

        elif categoria == "Roles":

            texto = """
⬛ **Roles**

`/addrole` • `s!addrole`
> Administrar roles

`/reactionroles` • `s!reactionroles`
> Roles con botones

`/createrole` • `s!createrole`
> Crear roles

`/deleterole` • `s!deleterole`
> Eliminar roles
"""

        # ====================================================
        # SERVIDOR
        # ====================================================

        else:

            texto = """
⬛ **Servidor**

`/config` • `s!config`
> Configuración

`/reglas` 
> Sistema de reglas

`/verification` • `s!verification`
> Sistema de verificación

`/server_setup` • `s!server_setup`
> Configuración del servidor
"""

        embed = discord.Embed(
            title=f"💜 {categoria}",
            description=texto,
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text="💜 Purple Bot System"
        )

        await interaction.response.edit_message(
            embed=embed
        )


# ============================================================
# VIEW DE AYUDA
# ============================================================

class HelpView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            HelpSelect()
        )


# ============================================================
# COG HELP
# ============================================================

class Help(commands.Cog):

    def __init__(
        self,
        bot
    ):
        self.bot = bot

    # ========================================================
    # /help
    # s!help
    # ========================================================

    @commands.hybrid_command(
        name="help",
        description="Panel de ayuda del bot"
    )
    async def help(
        self,
        ctx: commands.Context
    ):

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="⬛💜 Panel de Ayuda",
            description=f"""
╭━━━━━━━━━━━━━━╮
💜 **Bienvenido al centro de comandos**

👤 Usuario:
{ctx.author.mention}

🤖 Bot:
`{self.bot.user.name}`

⬛━━━━━━━━━━━━━━⬛

Seleccioná una categoría
en el menú de abajo.

╰━━━━━━━━━━━━━━╯
""",
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        # ====================================================
        # THUMBNAIL
        # ====================================================

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        # ====================================================
        # FOOTER
        # ====================================================

        embed.set_footer(
            text="💜 Purple Edition"
        )

        # ====================================================
        # ENVIAR
        # ====================================================

        await ctx.send(
            embed=embed,
            view=HelpView()
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Help(bot)
    )