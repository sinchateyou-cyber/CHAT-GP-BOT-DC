import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

# ID DEL ROL STAFF
STAFF_ROLE_ID = 1534413104908075049

# SI TAMBIÉN QUERÉS QUE OWNER TENGA ACCESO A LOS TICKETS,
# PONÉ ACÁ EL ID DEL ROL OWNER.
# Si no querés usarlo, dejalo en None.
OWNER_ROLE_ID = 1534413080698683474

# Nombre de la categoría
TICKET_CATEGORY_NAME = "🎫・TICKETS"


# ============================================================
# UTILIDADES
# ============================================================

def get_staff_role(guild: discord.Guild):
    return guild.get_role(STAFF_ROLE_ID)


def get_owner_role(guild: discord.Guild):
    if OWNER_ROLE_ID is None:
        return None

    return guild.get_role(OWNER_ROLE_ID)


def get_ticket_category(guild: discord.Guild):
    return discord.utils.get(
        guild.categories,
        name=TICKET_CATEGORY_NAME
    )


def is_ticket_channel(channel):
    return (
        isinstance(channel, discord.TextChannel)
        and channel.topic
        and channel.topic.startswith("ticket_owner:")
    )


def get_ticket_owner_id(channel):
    if not is_ticket_channel(channel):
        return None

    try:
        return int(
            channel.topic.replace(
                "ticket_owner:",
                "",
                1
            )
        )
    except (ValueError, TypeError):
        return None


def user_has_staff_access(
    interaction: discord.Interaction
):
    if interaction.guild is None:
        return False

    member = interaction.user

    # Administrador
    if member.guild_permissions.administrator:
        return True

    # Staff
    staff_role = get_staff_role(
        interaction.guild
    )

    if staff_role and staff_role in member.roles:
        return True

    # Owner
    owner_role = get_owner_role(
        interaction.guild
    )

    if owner_role and owner_role in member.roles:
        return True

    return False


# ============================================================
# VIEW ABRIR TICKET
# ============================================================

class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Abrir Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="tickets:open"
    )
    async def abrir_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user

        if guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return

        # ====================================================
        # COMPROBAR SI YA TIENE TICKET
        # ====================================================

        for channel in guild.text_channels:

            if channel.topic == f"ticket_owner:{user.id}":

                await interaction.response.send_message(
                    f"❌ Ya tenés un ticket abierto: {channel.mention}",
                    ephemeral=True
                )
                return

        # ====================================================
        # CATEGORÍA
        # ====================================================

        category = get_ticket_category(guild)

        try:

            if category is None:

                category = await guild.create_category(
                    name=TICKET_CATEGORY_NAME,
                    reason="Sistema de tickets"
                )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permiso para crear la categoría de tickets.\n"
                "Necesito **Gestionar canales**.",
                ephemeral=True
            )
            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                "❌ Discord rechazó la creación de la categoría.\n"
                f"`{error}`",
                ephemeral=True
            )
            return

        # ====================================================
        # ROLES
        # ====================================================

        staff_role = get_staff_role(guild)
        owner_role = get_owner_role(guild)

        # ====================================================
        # PERMISOS
        # ====================================================

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
        }

        # ====================================================
        # BOT
        # ====================================================

        bot_member = guild.me

        if bot_member:

            overwrites[bot_member] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True,
                manage_permissions=True,
                attach_files=True,
                embed_links=True
            )

        # ====================================================
        # STAFF
        # ====================================================

        if staff_role:

            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        # ====================================================
        # OWNER
        # ====================================================

        if owner_role:

            overwrites[owner_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True
            )

        # ====================================================
        # NOMBRE DEL TICKET
        # ====================================================

        safe_name = "".join(
            character
            for character in user.name.lower()
            if character.isalnum()
            or character in "-_"
        )

        if not safe_name:
            safe_name = f"user-{user.id}"

        channel_name = f"ticket-{safe_name}"

        existing = discord.utils.get(
            category.channels,
            name=channel_name
        )

        if existing:
            channel_name = f"ticket-{user.id}"

        # ====================================================
        # CREAR CANAL
        # ====================================================

        try:

            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                topic=f"ticket_owner:{user.id}",
                overwrites=overwrites,
                reason=f"Ticket creado por {user}"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No puedo crear el ticket.\n\n"
                "Revisá que mi rol tenga:\n"
                "• Gestionar canales\n"
                "• Gestionar permisos\n"
                "• Ver canales",
                ephemeral=True
            )
            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                "❌ Discord rechazó la creación del ticket.\n"
                f"`{error}`",
                ephemeral=True
            )
            return

        # ====================================================
        # EMBED DEL TICKET
        # ====================================================

        embed = discord.Embed(
            title="🎫・TICKET ABIERTO",
            description=(
                f"Bienvenido/a {user.mention}.\n\n"
                "Tu ticket fue creado correctamente.\n"
                "Un miembro del **Staff** te va a atender.\n\n"
                "🔒 **Este canal es privado.**\n"
                "📩 Explicá tu problema con todos los detalles posibles.\n"
                "📎 Podés enviar imágenes y archivos.\n\n"
                "Cuando termines, presioná **Cerrar Ticket**."
            ),
            color=discord.Color.from_rgb(
                145,
                70,
                255
            )
        )

        embed.add_field(
            name="👤 Usuario",
            value=user.mention,
            inline=True
        )

        embed.add_field(
            name="🛠️ Staff",
            value=(
                staff_role.mention
                if staff_role
                else "Staff"
            ),
            inline=True
        )

        if owner_role:

            embed.add_field(
                name="👑 Owner",
                value=owner_role.mention,
                inline=True
            )

        embed.set_footer(
            text=f"{guild.name} • Sistema de Tickets"
        )

        # ====================================================
        # ENVIAR MENSAJE INICIAL
        # ====================================================

        try:

            await channel.send(
                content=user.mention,
                embed=embed,
                view=CloseTicketView()
            )

        except discord.HTTPException:

            try:
                await channel.delete(
                    reason="No se pudo enviar el mensaje inicial"
                )
            except discord.HTTPException:
                pass

            await interaction.response.send_message(
                "❌ El canal se creó, "
                "pero no pude enviar el mensaje inicial.",
                ephemeral=True
            )
            return

        # ====================================================
        # RESPUESTA
        # ====================================================

        await interaction.response.send_message(
            f"✅ **Ticket creado correctamente:** {channel.mention}",
            ephemeral=True
        )


# ============================================================
# VIEW CERRAR TICKET
# ============================================================

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=None
        )

    @discord.ui.button(
        label="Cerrar Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="tickets:close"
    )
    async def cerrar_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = interaction.channel

        if not is_ticket_channel(channel):

            await interaction.response.send_message(
                "❌ Este canal no es un ticket.",
                ephemeral=True
            )
            return

        # ====================================================
        # PERMITIR AL DUEÑO O STAFF
        # ====================================================

        owner_id = get_ticket_owner_id(channel)

        is_owner = (
            owner_id == interaction.user.id
        )

        is_staff = user_has_staff_access(
            interaction
        )

        if not is_owner and not is_staff:

            await interaction.response.send_message(
                "❌ No tenés permiso para cerrar este ticket.",
                ephemeral=True
            )
            return

        # ====================================================
        # CONFIRMACIÓN
        # ====================================================

        embed = discord.Embed(
            title="🔒・CERRAR TICKET",
            description=(
                "¿Estás seguro de que querés cerrar este ticket?\n\n"
                "⚠️ **El canal será eliminado permanentemente.**"
            ),
            color=discord.Color.red()
        )

        await interaction.response.send_message(
            embed=embed,
            view=ConfirmCloseView(),
            ephemeral=True
        )


# ============================================================
# CONFIRMAR CIERRE
# ============================================================

class ConfirmCloseView(discord.ui.View):

    def __init__(self):
        super().__init__(
            timeout=60
        )

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

        if channel is None:
            return

        if not is_ticket_channel(channel):

            await interaction.response.send_message(
                "❌ Este canal ya no es un ticket.",
                ephemeral=True
            )
            return

        owner_id = get_ticket_owner_id(
            channel
        )

        is_owner = (
            owner_id == interaction.user.id
        )

        is_staff = user_has_staff_access(
            interaction
        )

        if not is_owner and not is_staff:

            await interaction.response.send_message(
                "❌ No tenés permiso para cerrar este ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔒 **Cerrando ticket...**"
        )

        try:

            await channel.delete(
                reason=f"Ticket cerrado por {interaction.user}"
            )

        except discord.Forbidden:

            try:
                await interaction.followup.send(
                    "❌ No tengo permiso para eliminar este canal.",
                    ephemeral=True
                )
            except discord.HTTPException:
                pass

        except discord.HTTPException:

            try:
                await interaction.followup.send(
                    "❌ Discord rechazó la eliminación del canal.",
                    ephemeral=True
                )
            except discord.HTTPException:
                pass

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
            content="❌ **Cierre cancelado.**",
            embed=None,
            view=None
        )


# ============================================================
# COG
# ============================================================

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /TICKET
    # ========================================================

    @app_commands.command(
        name="ticket",
        description="Envía el panel de tickets."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def ticket(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solamente funciona en un servidor.",
                ephemeral=True
            )
            return

        if interaction.channel is None:

            await interaction.response.send_message(
                "❌ No se puede usar este comando acá.",
                ephemeral=True
            )
            return

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="🎫・SOPORTE PRIVADO",
            description=(
                "**¿Necesitás ayuda?**\n\n"
                "Abrí un ticket para comunicarte "
                "directamente con el equipo de **Staff**.\n\n"
                "🔒 **Ticket privado**\n"
                "👤 Solo vos y el Staff podrán verlo.\n"
                "📩 Podés enviar imágenes y archivos.\n"
                "⚡ Atención rápida y privada.\n\n"
                "**Presioná el botón de abajo para abrir tu ticket.**"
            ),
            color=discord.Color.from_rgb(
                145,
                70,
                255
            )
        )

        embed.set_footer(
            text=f"{interaction.guild.name} • Sistema de Tickets"
        )

        # ====================================================
        # ENVIAR PANEL
        # ====================================================

        await interaction.channel.send(
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            "✅ **Panel de tickets enviado correctamente.**",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    # Registrar las Views persistentes.
    bot.add_view(
        TicketView()
    )

    bot.add_view(
        CloseTicketView()
    )

    await bot.add_cog(
        Tickets(bot)
    )