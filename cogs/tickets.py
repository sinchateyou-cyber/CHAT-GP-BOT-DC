import discord
from discord.ext import commands
from discord import app_commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
STAFF_ROLE_NAME = "Staff"
TICKET_CATEGORY_NAME = "🎫・TICKETS"
# ============================================================
# UTILIDADES
# ============================================================
def get_staff_role(guild: discord.Guild):
    return discord.utils.get(
        guild.roles,
        name=STAFF_ROLE_NAME
    )
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
        # BUSCAR TICKET EXISTENTE
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
                "❌ No tengo permiso para crear la categoría de tickets.",
                ephemeral=True
            )
            return
        except discord.HTTPException as error:
            await interaction.response.send_message(
                f"❌ Discord rechazó la creación de la categoría.\n`{error}`",
                ephemeral=True
            )
            return
        # ====================================================
        # STAFF
        # ====================================================
        staff_role = get_staff_role(guild)
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
        # NOMBRE
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
                "❌ No puedo crear el ticket.\n"
                "Revisá que mi bot tenga **Gestionar canales**.",
                ephemeral=True
            )
            return
        except discord.HTTPException as error:
            await interaction.response.send_message(
                f"❌ Discord rechazó la creación del ticket.\n"
                f"`{error}`",
                ephemeral=True
            )
            return
        # ====================================================
        # EMBED
        # ====================================================
        embed = discord.Embed(
            title="🎫・TICKET ABIERTO",
            description=(
                f"Bienvenido/a {user.mention}.\n\n"
                "Tu ticket fue creado correctamente.\n"
                "Un miembro del **Staff** te va a atender.\n\n"
                "🔒 **Este canal es privado.**\n"
                "📩 Explicá tu problema con todos los detalles posibles.\n\n"
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
        embed.set_footer(
            text="Sistema de Tickets • Soporte"
        )
        # ====================================================
        # ENVIAR MENSAJE
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
            except:
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
# VIEW CERRAR
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
            except:
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
        # ====================================================
        # COMPROBAR CANAL
        # ====================================================
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
                "📩 Podés enviar imágenes y archivos.\n\n"
                "**Presioná el botón de abajo para abrir tu ticket.**"
            ),
            color=discord.Color.from_rgb(
                145,
                70,
                255
            )
        )
        embed.set_footer(
            text="Sistema de Tickets"
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
    await bot.add_cog(
        Tickets(bot)
    )