import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

STAFF_ROLE_NAME = "Staff"
TICKET_CATEGORY_NAME = "🎫・TICKETS"


# ============================================================
# VISTA DEL TICKET
# ============================================================

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="ticket:abrir"
    )
    async def abrir_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild
        user = interaction.user

        if guild is None:
            return

        # ----------------------------------------------------
        # Buscar si ya tiene un ticket
        # ----------------------------------------------------

        for channel in guild.text_channels:
            if channel.topic == f"ticket_owner:{user.id}":
                return await interaction.response.send_message(
                    f"❌ Ya tenés un ticket abierto: {channel.mention}",
                    ephemeral=True
                )

        # ----------------------------------------------------
        # Buscar categoría
        # ----------------------------------------------------

        category = discord.utils.get(
            guild.categories,
            name=TICKET_CATEGORY_NAME
        )

        if category is None:
            category = await guild.create_category(
                TICKET_CATEGORY_NAME,
                reason="Creación de categoría de tickets"
            )

        # ----------------------------------------------------
        # Buscar rol Staff
        # ----------------------------------------------------

        staff_role = discord.utils.get(
            guild.roles,
            name=STAFF_ROLE_NAME
        )

        # ----------------------------------------------------
        # Permisos privados
        # ----------------------------------------------------

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            ),

            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True
            )
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True
            )

        # ----------------------------------------------------
        # Crear canal
        # ----------------------------------------------------

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}".lower().replace(" ", "-"),
            category=category,
            topic=f"ticket_owner:{user.id}",
            overwrites=overwrites,
            reason=f"Ticket creado por {user}"
        )

        # ----------------------------------------------------
        # Embed
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🎫 Ticket abierto",
            description=(
                f"Qué onda, {user.mention}.\n\n"
                "Tu ticket fue creado correctamente.\n"
                "Un miembro del **Staff** te va a atender "
                "cuando pueda.\n\n"
                "🔒 Este canal es **privado**."
            ),
            color=discord.Color.from_rgb(128, 0, 255)
        )

        embed.set_footer(
            text="Soporte • Ticket privado"
        )

        await channel.send(
            content=user.mention,
            embed=embed,
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket creado: {channel.mention}",
            ephemeral=True
        )


# ============================================================
# VISTA PARA CERRAR
# ============================================================

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Cerrar Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="ticket:cerrar"
    )
    async def cerrar_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.channel:
            return

        embed = discord.Embed(
            title="🔒 Cerrar ticket",
            description=(
                "¿Estás seguro de que querés cerrar este ticket?\n\n"
                "Esta acción eliminará el canal."
            ),
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ConfirmCloseView(),
            ephemeral=True
        )


# ============================================================
# CONFIRMACIÓN
# ============================================================

class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(
        label="Sí, cerrar",
        emoji="🔒",
        style=discord.ButtonStyle.danger
    )
    async def confirmar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = interaction.channel

        await interaction.response.send_message(
            "🔒 Cerrando ticket..."
        )

        await channel.delete(
            reason=f"Ticket cerrado por {interaction.user}"
        )

    @discord.ui.button(
        label="Cancelar",
        emoji="❌",
        style=discord.ButtonStyle.secondary
    )
    async def cancelar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            content="❌ Cierre cancelado.",
            embed=None,
            view=None
        )


# ============================================================
# COG
# ============================================================

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # --------------------------------------------------------
    # /ticket
    # --------------------------------------------------------

    @app_commands.command(
        name="ticket",
        description="Envía el panel de tickets privados."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def ticket(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🎫 SOPORTE PRIVADO",
            description=(
                "¿Necesitás ayuda?\n\n"
                "Abrí un ticket para hablar directamente "
                "con el equipo de **Staff**.\n\n"
                "🔒 **Tu ticket será completamente privado.**\n"
                "👤 Solo vos y el Staff podrán verlo.\n\n"
                "Presioná el botón de abajo para abrir uno."
            ),
            color=discord.Color.from_rgb(128, 0, 255)
        )

        embed.set_footer(
            text="Sistema de Tickets"
        )

        await interaction.channel.send(
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            "✅ Panel de tickets enviado.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Tickets(bot))