import discord
from discord.ext import commands
from discord import app_commands


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


        if categoria == "Moderación":

            texto = """
⬛ **Moderación**

`/ban`
> Banear usuarios

`/kick`
> Expulsar usuarios

`/timeout`
> Silenciar usuarios

`/clear`
> Limpiar mensajes

`/lock`
> Bloquear canales
"""


        elif categoria == "Utilidades":

            texto = """
⬛ **Utilidades**

`/avatar`
> Ver avatar

`/userinfo`
> Información del usuario

`/botinfo`
> Información del bot

`/ping`
> Ver latencia
"""


        elif categoria == "Roles":

            texto = """
⬛ **Roles**

`/roles`
> Panel de roles

`/addrole`
> Crear roles

`/reactionroles`
> Roles con botones
"""


        else:

            texto = """
⬛ **Servidor**

`/config`
> Configuración

`/reglas`
> Sistema de reglas

`/verification`
> Sistema de verificación
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


class HelpView(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            HelpSelect()
        )



class Help(commands.Cog):

    def __init__(
        self,
        bot
    ):
        self.bot = bot


    @app_commands.command(
        name="help",
        description="Panel de ayuda del bot"
    )
    async def help(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="⬛💜 Panel de Ayuda",
            description=f"""
╭━━━━━━━━━━━━━━╮
💜 **Bienvenido al centro de comandos**

👤 Usuario:
{interaction.user.mention}

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


        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )


        embed.set_footer(
            text="💜 Purple Edition"
        )


        await interaction.response.send_message(
            embed=embed,
            view=HelpView()
        )


async def setup(bot):
    await bot.add_cog(
        Help(bot)
    )