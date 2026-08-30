import json
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "alliances.json"

PURPLE = discord.Color.from_rgb(138, 43, 226)


# ============================================================
# DATOS
# ============================================================

def load_data():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")
        return {}

    try:
        return json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def save_data(data):
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# MODAL DE ALIANZA
# ============================================================

class AllianceModal(discord.ui.Modal, title="🤝 Solicitar alianza"):

    server_name = discord.ui.TextInput(
        label="Nombre del servidor",
        placeholder="Ej: Mi Comunidad",
        max_length=100,
        required=True
    )

    invite = discord.ui.TextInput(
        label="Invitación de Discord",
        placeholder="https://discord.gg/xxxxx",
        max_length=200,
        required=True
    )

    description = discord.ui.TextInput(
        label="Descripción",
        placeholder="Contanos brevemente sobre tu servidor.",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        cog = interaction.client.get_cog("Alliances")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema de alianzas no está disponible.",
                ephemeral=True
            )

        await cog.send_alliance_request(
            interaction,
            self.server_name.value,
            self.invite.value,
            self.description.value
        )


# ============================================================
# VISTA DE SOLICITUD
# ============================================================

class AllianceRequestView(discord.ui.View):

    def __init__(
        self,
        request_id: str
    ):
        super().__init__(
            timeout=None
        )

        self.request_id = request_id

    @discord.ui.button(
        label="Aceptar",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        cog = interaction.client.get_cog("Alliances")

        if cog is None:
            return await interaction.response.send_message(
                "❌ Sistema no disponible.",
                ephemeral=True
            )

        await cog.accept_request(
            interaction,
            self.request_id
        )

    @discord.ui.button(
        label="Rechazar",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        cog = interaction.client.get_cog("Alliances")

        if cog is None:
            return await interaction.response.send_message(
                "❌ Sistema no disponible.",
                ephemeral=True
            )

        await cog.reject_request(
            interaction,
            self.request_id
        )


# ============================================================
# COG
# ============================================================

class Alliances(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.data = load_data()

    # ========================================================
    # CARGAR
    # ========================================================

    async def cog_load(self):

        print("🤝 Alliances iniciado correctamente.")

        # Restaurar botones de solicitudes pendientes
        pending = self.data.get(
            "pending_requests",
            {}
        )

        for request_id, request in pending.items():

            try:

                self.bot.add_view(
                    AllianceRequestView(
                        request_id
                    ),
                    message_id=int(
                        request["message_id"]
                    )
                )

            except Exception as error:

                print(
                    f"⚠️ No pude restaurar alianza "
                    f"{request_id}: {error}"
                )

    # ========================================================
    # PERMISOS
    # ========================================================

    def can_manage(
        self,
        member: discord.Member
    ):

        return (
            member.guild_permissions.administrator
            or member.guild_permissions.manage_guild
        )

    # ========================================================
    # CONFIGURAR ALIANZAS
    # ========================================================

    @app_commands.command(
        name="configalianzas",
        description="Configura los canales del sistema de alianzas."
    )
    @app_commands.describe(
        solicitudes="Canal donde llegarán las solicitudes.",
        publicaciones="Canal donde se publicarán las alianzas aceptadas."
    )
    async def configalianzas(
        self,
        interaction: discord.Interaction,
        solicitudes: discord.TextChannel,
        publicaciones: discord.TextChannel
    ):

        if not self.can_manage(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás tener **Gestionar servidor** para usar este comando.",
                ephemeral=True
            )

        guild_id = str(
            interaction.guild.id
        )

        guild_data = self.data.setdefault(
            "guilds",
            {}
        )

        guild_data[guild_id] = {
            "requests_channel_id": solicitudes.id,
            "public_channel_id": publicaciones.id
        }

        save_data(
            self.data
        )

        embed = discord.Embed(
            title="⚙️ Configuración de alianzas",
            description=(
                "El sistema quedó configurado correctamente.\n\n"
                f"📩 **Solicitudes:** {solicitudes.mention}\n"
                f"🤝 **Publicaciones:** {publicaciones.mention}"
            ),
            color=PURPLE
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # SOLICITAR ALIANZA
    # ========================================================

    @app_commands.command(
        name="alianza",
        description="Envía una solicitud de alianza."
    )
    async def alianza(
        self,
        interaction: discord.Interaction
    ):

        if not self.can_manage(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás tener **Gestionar servidor** para solicitar una alianza.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            AllianceModal()
        )

    # ========================================================
    # ENVIAR SOLICITUD
    # ========================================================

    async def send_alliance_request(
        self,
        interaction,
        server_name,
        invite,
        description
    ):

        guild = interaction.guild

        if guild is None:
            return await interaction.response.send_message(
                "❌ Esto solo funciona dentro de un servidor.",
                ephemeral=True
            )

        guilds_data = self.data.setdefault(
            "guilds",
            {}
        )

        config = guilds_data.get(
            str(guild.id)
        )

        if not config:

            return await interaction.response.send_message(
                "❌ El sistema todavía no está configurado.\n\n"
                "Un administrador debe usar `/configalianzas`.",
                ephemeral=True
            )

        channel = guild.get_channel(
            config["requests_channel_id"]
        )

        if channel is None:

            return await interaction.response.send_message(
                "❌ No encontré el canal de solicitudes.",
                ephemeral=True
            )

        if not invite.startswith(
            (
                "https://discord.gg/",
                "https://discord.com/invite/"
            )
        ):

            return await interaction.response.send_message(
                "❌ La invitación de Discord no es válida.",
                ephemeral=True
            )

        # ====================================================
        # ID ÚNICO
        # ====================================================

        request_id = (
            f"{guild.id}-"
            f"{interaction.user.id}-"
            f"{interaction.id}"
        )

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="🤝 NUEVA SOLICITUD DE ALIANZA",
            color=PURPLE
        )

        embed.add_field(
            name="🏷️ Servidor",
            value=f"**{server_name}**",
            inline=False
        )

        embed.add_field(
            name="👤 Solicitante",
            value=interaction.user.mention,
            inline=True
        )

        embed.add_field(
            name="🏠 Servidor de origen",
            value=guild.name,
            inline=True
        )

        embed.add_field(
            name="📝 Descripción",
            value=description,
            inline=False
        )

        embed.add_field(
            name="🔗 Invitación",
            value=invite,
            inline=False
        )

        if guild.icon:

            embed.set_thumbnail(
                url=guild.icon.url
            )

        embed.set_footer(
            text="Sistema de alianzas"
        )

        # ====================================================
        # VIEW
        # ====================================================

        view = AllianceRequestView(
            request_id
        )

        try:

            message = await channel.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes en ese canal.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            return await interaction.response.send_message(
                f"❌ Discord rechazó el mensaje.\n`{error}`",
                ephemeral=True
            )

        # ====================================================
        # GUARDAR
        # ====================================================

        pending = self.data.setdefault(
            "pending_requests",
            {}
        )

        pending[request_id] = {

            "guild_id":
                guild.id,

            "user_id":
                interaction.user.id,

            "server_name":
                server_name,

            "invite":
                invite,

            "description":
                description,

            "message_id":
                message.id,

            "channel_id":
                channel.id
        }

        save_data(
            self.data
        )

        await interaction.response.send_message(
            "✅ **Solicitud de alianza enviada correctamente.**",
            ephemeral=True
        )

    # ========================================================
    # ACEPTAR
    # ========================================================

    async def accept_request(
        self,
        interaction,
        request_id
    ):

        if not self.can_manage(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás **Gestionar servidor** para aceptar alianzas.",
                ephemeral=True
            )

        pending = self.data.get(
            "pending_requests",
            {}
        )

        request = pending.get(
            request_id
        )

        if request is None:

            return await interaction.response.send_message(
                "❌ Esta solicitud ya no existe.",
                ephemeral=True
            )

        guild = interaction.guild

        # ====================================================
        # CONFIG
        # ====================================================

        config = self.data.get(
            "guilds",
            {}
        ).get(
            str(guild.id),
            {}
        )

        public_channel_id = config.get(
            "public_channel_id"
        )

        public_channel = None

        if public_channel_id:

            public_channel = guild.get_channel(
                public_channel_id
            )

        # ====================================================
        # GUARDAR ALIANZA
        # ====================================================

        alliances = self.data.setdefault(
            "alliances",
            {}
        )

        guild_alliances = alliances.setdefault(
            str(guild.id),
            []
        )

        alliance_data = {

            "server_name":
                request["server_name"],

            "invite":
                request["invite"],

            "description":
                request["description"],

            "origin_guild_id":
                request["guild_id"],

            "user_id":
                request["user_id"]
        }

        guild_alliances.append(
            alliance_data
        )

        # Eliminar pendiente
        del pending[request_id]

        save_data(
            self.data
        )

        # ====================================================
        # PUBLICAR ALIANZA
        # ====================================================

        if public_channel:

            origin_guild = self.bot.get_guild(
                request["guild_id"]
            )

            embed = discord.Embed(
                title="🤝 NUEVA ALIANZA",
                description=(
                    f"💜 **{request['server_name']}**\n\n"
                    f"{request['description']}\n\n"
                    f"🔗 **[ENTRAR AL SERVIDOR]"
                    f"({request['invite']})**"
                ),
                color=PURPLE
            )

            if origin_guild:

                if origin_guild.icon:

                    embed.set_thumbnail(
                        url=origin_guild.icon.url
                    )

                embed.add_field(
                    name="👥 Miembros",
                    value=(
                        f"**{origin_guild.member_count or '?'}**"
                    ),
                    inline=True
                )

            embed.add_field(
                name="🤝 Estado",
                value="**Alianza oficial**",
                inline=True
            )

            embed.set_footer(
                text=(
                    f"{guild.name} × "
                    f"{request['server_name']}"
                )
            )

            try:

                await public_channel.send(
                    embed=embed
                )

            except discord.Forbidden:

                print(
                    "⚠️ No pude publicar la alianza: "
                    "faltan permisos."
                )

        # ====================================================
        # EDITAR SOLICITUD
        # ====================================================

        try:

            if interaction.message.embeds:

                embed = interaction.message.embeds[0]

                embed.title = "🤝 ALIANZA ACEPTADA"
                embed.color = discord.Color.green()

                embed.add_field(
                    name="Estado",
                    value="✅ **ACEPTADA**",
                    inline=False
                )

                await interaction.message.edit(
                    embed=embed,
                    view=None
                )

        except Exception:
            pass

        await interaction.response.send_message(
            "🤝 **Alianza aceptada correctamente.**\n"
            "La alianza fue publicada automáticamente.",
            ephemeral=True
        )

        # ====================================================
        # AVISAR
        # ====================================================

        origin_guild = self.bot.get_guild(
            request["guild_id"]
        )

        if origin_guild:

            member = origin_guild.get_member(
                request["user_id"]
            )

            if member:

                try:

                    await member.send(
                        f"🤝 **¡Tu alianza con "
                        f"{guild.name} fue aceptada!**\n\n"
                        "La alianza ya fue publicada."
                    )

                except discord.Forbidden:
                    pass

    # ========================================================
    # RECHAZAR
    # ========================================================

    async def reject_request(
        self,
        interaction,
        request_id
    ):

        if not self.can_manage(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás **Gestionar servidor** para rechazar alianzas.",
                ephemeral=True
            )

        pending = self.data.get(
            "pending_requests",
            {}
        )

        request = pending.get(
            request_id
        )

        if request is None:

            return await interaction.response.send_message(
                "❌ Esta solicitud ya no existe.",
                ephemeral=True
            )

        del pending[request_id]

        save_data(
            self.data
        )

        try:

            if interaction.message.embeds:

                embed = interaction.message.embeds[0]

                embed.title = "❌ ALIANZA RECHAZADA"
                embed.color = discord.Color.red()

                embed.add_field(
                    name="Estado",
                    value="❌ **RECHAZADA**",
                    inline=False
                )

                await interaction.message.edit(
                    embed=embed,
                    view=None
                )

        except Exception:
            pass

        await interaction.response.send_message(
            "❌ **Solicitud de alianza rechazada.**",
            ephemeral=True
        )

        # ====================================================
        # AVISAR
        # ====================================================

        origin_guild = self.bot.get_guild(
            request["guild_id"]
        )

        if origin_guild:

            member = origin_guild.get_member(
                request["user_id"]
            )

            if member:

                try:

                    await member.send(
                        f"❌ **Tu solicitud de alianza con "
                        f"{interaction.guild.name} fue rechazada.**"
                    )

                except discord.Forbidden:
                    pass

    # ========================================================
    # LISTAR ALIANZAS
    # ========================================================

    @app_commands.command(
        name="alianzas",
        description="Muestra las alianzas oficiales."
    )
    async def alianzas(
        self,
        interaction: discord.Interaction
    ):

        alliances = self.data.get(
            "alliances",
            {}
        ).get(
            str(interaction.guild.id),
            []
        )

        if not alliances:

            return await interaction.response.send_message(
                "🤝 **Este servidor todavía no tiene alianzas oficiales.**",
                ephemeral=True
            )

        description = ""

        for alliance in alliances:

            description += (
                f"🤝 **{alliance['server_name']}**\n"
                f"🔗 {alliance['invite']}\n\n"
            )

        embed = discord.Embed(
            title="🤝 ALIANZAS OFICIALES",
            description=description,
            color=PURPLE
        )

        await interaction.response.send_message(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Alliances(bot)
    )