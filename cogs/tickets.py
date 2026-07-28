import discord
from discord.ext import commands


class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Crear Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.green,
        custom_id="crear_ticket"
    )
    async def crear_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        usuario = interaction.user

        # Buscar si ya tiene un ticket
        ticket_existente = discord.utils.get(
            guild.text_channels,
            name=f"ticket-{usuario.id}"
        )

        if ticket_existente:

            await interaction.response.send_message(
                f"❌ Ya tenés un ticket abierto: "
                f"{ticket_existente.mention}",
                ephemeral=True
            )

            return

        # Crear permisos
        permisos = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            usuario: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        # Crear canal
        canal = await guild.create_text_channel(
            name=f"ticket-{usuario.id}",
            overwrites=permisos
        )

        await interaction.response.send_message(
            f"🎫 Ticket creado: {canal.mention}",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🎫 Ticket de soporte",
            description=(
                f"Hola {usuario.mention} 👋\n\n"
                "Explicá tu problema y un miembro "
                "del staff te ayudará."
            )
        )

        embed.set_footer(
            text="Usá !closeticket para cerrar el ticket."
        )

        await canal.send(
            content=usuario.mention,
            embed=embed
        )


class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PANEL DE TICKETS
    # =========================

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def ticketpanel(self, ctx):

        embed = discord.Embed(
            title="🎫 Centro de Soporte",
            description=(
                "¿Necesitás ayuda?\n\n"
                "Presioná el botón de abajo "
                "para crear un ticket privado "
                "con el equipo de soporte."
            )
        )

        embed.set_footer(
            text="Un ticket por usuario."
        )

        await ctx.send(
            embed=embed,
            view=TicketView()
        )

    # =========================
    # CERRAR TICKET
    # =========================

    @commands.command()
    async def closeticket(self, ctx):

        if not ctx.channel.name.startswith(
            "ticket-"
        ):
            await ctx.send(
                "❌ Este comando solo puede "
                "usarse dentro de un ticket."
            )

            return

        await ctx.send(
            "🔒 Este ticket se cerrará "
            "en 5 segundos..."
        )

        await discord.utils.sleep_until(
            discord.utils.utcnow()
            + discord.utils.timedelta(seconds=5)
        )

        await ctx.channel.delete()

    # =========================
    # ERRORES
    # =========================

    @ticketpanel.error
    async def ticketpanel_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás el permiso "
                "`Gestionar canales`."
            )

        else:

            print(
                f"❌ Error en tickets: {error}"
            )


async def setup(bot):

    await bot.add_cog(
        Tickets(bot)
    )

    # Registrar la vista para que el botón
    # siga funcionando después de reiniciar
    bot.add_view(
        TicketView()
    )