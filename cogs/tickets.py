import discord
from discord.ext import commands


class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=None
        )


    @discord.ui.button(
        label="Crear Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.green
    )
    async def crear_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild

        nombre = (
            f"ticket-{interaction.user.name}"
        )

        existente = discord.utils.get(
            guild.text_channels,
            name=nombre
        )

        if existente:
            await interaction.response.send_message(
                "❌ Ya tenés un ticket abierto.",
                ephemeral=True
            )
            return

        canal = await guild.create_text_channel(
            nombre
        )

        await canal.set_permissions(
            guild.default_role,
            view_channel=False
        )

        await canal.set_permissions(
            interaction.user,
            view_channel=True,
            send_messages=True
        )

        await interaction.response.send_message(
            f"🎫 Ticket creado: {canal.mention}",
            ephemeral=True
        )

        await canal.send(
            f"👋 Hola {interaction.user.mention}.\n"
            f"Un miembro del staff te atenderá pronto."
        )


class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def ticketpanel(self, ctx):

        embed = discord.Embed(
            title="🎫 Soporte",
            description=(
                "Presioná el botón para "
                "crear un ticket."
            )
        )

        await ctx.send(
            embed=embed,
            view=TicketView()
        )


    @commands.command()
    async def closeticket(self, ctx):

        if not ctx.channel.name.startswith(
            "ticket-"
        ):
            await ctx.send(
                "❌ Este canal no es un ticket."
            )
            return

        await ctx.send(
            "🔒 Cerrando ticket..."
        )

        await ctx.channel.delete()


async def setup(bot):
    await bot.add_cog(
        Tickets(bot)
    )