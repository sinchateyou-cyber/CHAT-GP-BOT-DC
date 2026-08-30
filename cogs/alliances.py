import json
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIG
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "alliances.json"

PURPLE = discord.Color.from_rgb(138, 43, 226)


# ============================================================
# DATOS
# ============================================================

def ensure_data():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def load_data():
    ensure_data()

    try:
        return json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def save_data(data):
    ensure_data()

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# MODAL
# ============================================================

class AllianceModal(discord.ui.Modal, title="🤝 Solicitar alianza"):

    servidor = discord.ui.TextInput(
        label="Nombre del servidor",
        placeholder="Ej: Mi Comunidad",
        max_length=100,
        required=True
    )

    invitacion = discord.ui.TextInput(
        label="Invitación de Discord",
        placeholder="https://discord.gg/xxxxx",
        max_length=200,
        required=True
    )

    descripcion = discord.ui.TextInput(
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
            self.servidor.value,
            self.invitacion.value,
            self.descripcion.value
        )


# ============================================================
# VISTA DE SOLICITUD
# ============================================================

class AllianceRequestView(discord.ui.View):

    def __init__(
        self,
        origin_guild_id: int,
        applicant_id: int,
        server_name: str,
        invite: str,
        description: str
    ):
        super().__init__(timeout=None)

        self.origin_guild_id = origin_guild_id
        self.applicant_id = applicant_id
        self.server_name = server_name
        self.invite = invite
        self.description = description

    @discord.ui.button(
        label="Aceptar",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="alliance:accept"
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

        await cog.accept_alliance(
            interaction,
            self.origin_guild_id,
            self.applicant_id,
            self.server_name,
            self.invite,
            self.description
        )

    @discord.ui.button(
        label="Rechazar",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="alliance:reject"
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

        await cog.reject_alliance(
            interaction,
            self.origin_guild_id,
            self.applicant_id
        )


# ============================================================
# COG
# ============================================================

class Alliances(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.data = load_data()

    async def cog_load():

        print("✅ Alliances cargado.")

    # ========================================================
    # PERMISOS
    # ========================================================

    def can_manage_alliance(
        self,
        member: discord.Member
    ):

        return (
            member.guild_permissions.manage_guild
            or member.guild_permissions.administrator
        )

    # ========================================================
    # CONFIGURAR CANALES
    # ========================================================

    @app_commands.command(
        name="configalianzas",
        description="Configura los canales del sistema de alianzas."
    )
    @app_commands.describe(
        solicitudes="Canal donde llegarán las solicitudes.",
        publicaciones="Canal donde se publicarán las alianzas aceptadas."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def configalianzas(
        self,
        interaction: discord.Interaction,
        solicitudes: discord.TextChannel,
        publicaciones: discord.TextChannel
    ):

        guild_id = str(
            interaction.guild.id
        )

        if guild_id not in self.data:
            self.data[guild_id] = {}

        self.data[guild_id]["requests_channel_id"] = solicitudes.id
        self.data[guild_id]["public_channel_id"] = publicaciones.id

        save_data(self.data)

        embed = discord.Embed(
            title="⚙️ Configuración de alianzas",
            description=(
                "El sistema de alianzas fue configurado correctamente.\n\n"
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

        if not self.can_manage_alliance(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás **Gestionar servidor** para solicitar una alianza.",
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

        guild_data = self.data.get(
            str(guild.id),
            {}
        )

        channel_id = guild_data.get(
            "requests_channel_id"
        )

        if not channel_id:

            return await interaction.response.send_message(
                "❌ El sistema de alianzas todavía no está configurado.\n\n"
                "Un administrador debe usar `/configalianzas`.",
                ephemeral=True
            )

        channel = guild.get_channel(
            channel_id
        )

        if channel is None:

            return await interaction.response.send_message(
                "❌ No encontré el canal de solicitudes.",
                ephemeral=True
            )

        if "discord.gg/" not in invite.lower():

            return await interaction.response.send_message(
                "❌ La invitación de Discord no parece válida.",
                ephemeral=True
            )

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="🤝 NUEVA SOLICITUD DE ALIANZA",
            description=(
                f"🏷️ **Servidor:** {server_name}\n"
                f"👤 **Solicitante:** {interaction.user.mention}\n\n"
                f"📝 **Descripción**\n"
                f"{description}\n\n"
                f"🔗 **Invitación**\n"
                f"{invite}"
            ),
            color=PURPLE
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        embed.set_footer(
            text=f"Solicitud desde {guild.name}"
        )

        view = AllianceRequestView(
            guild.id,
            interaction.user.id,
            server_name,
            invite,
            description
        )

        try:

            await channel.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes en ese canal.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "✅ **Solicitud de alianza enviada correctamente.**",
            ephemeral=True
        )

    # ========================================================
    # ACEPTAR ALIANZA
    # ========================================================

    async def accept_alliance(
        self,
        interaction,
        origin_guild_id,
        applicant_id,
        server_name,
        invite,
        description
    ):

        if not self.can_manage_alliance(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás **Gestionar servidor** para aceptar alianzas.",
                ephemeral=True
            )

        guild = interaction.guild

        guild_data = self.data.setdefault(
            str(guild.id),
            {}
        )

        alliances = guild_data.setdefault(
            "alliances",
            []
        )

        # Evitar duplicados.
        if origin_guild_id not in alliances:

            alliances.append(
                origin_guild_id
            )

        save_data(self.data)

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

        # ====================================================
        # BUSCAR CANAL PÚBLICO
        # ====================================================

        public_channel_id = guild_data.get(
            "public_channel_id"
        )

        public_channel = None

        if public_channel_id:

            public_channel = guild.get_channel(
                public_channel_id
            )

        # ====================================================
        # PUBLICACIÓN
        # ====================================================

        if public_channel:

            origin_guild = self.bot.get_guild(
                origin_guild_id
            )

            # ------------------------------------------------
            # Crear embed público
            # ------------------------------------------------

            public_embed = discord.Embed(
                title="🤝 NUEVA ALIANZA",
                description=(
                    f"💜 **{server_name}**\n\n"
                    f"{description}\n\n"
                    f"🔗 **[ ENTRAR AL SERVIDOR ]({invite})**"
                ),
                color=PURPLE
            )

            # Icono del servidor aliado.
            if origin_guild and origin_guild.icon:

                public_embed.set_thumbnail(
                    url=origin_guild.icon.url
                )

            public_embed.add_field(
                name="🤝 Estado",
                value="**Alianza oficial**",
                inline=True
            )

            if origin_guild:

                public_embed.add_field(
                    name="👥 Miembros",
                    value=f"**{origin_guild.member_count or '?'}**",
                    inline=True
                )

            public_embed.set_footer(
                text=f"{guild.name} × {server_name}"
            )

            try:

                await public_channel.send(
                    embed=public_embed
                )

            except discord.Forbidden:

                await interaction.response.send_message(
                    "⚠️ Alianza aceptada, pero no pude publicar "
                    "el anuncio porque no tengo permisos en el canal público.",
                    ephemeral=True
                )

                return

        # ====================================================
        # RESPUESTA
        # ====================================================

        await interaction.response.send_message(
            "🤝 **Alianza aceptada correctamente.**\n"
            "La alianza fue publicada en el canal público.",
            ephemeral=True
        )

        # ====================================================
        # AVISAR AL SOLICITANTE
        # ====================================================

        origin_guild = self.bot.get_guild(
            origin_guild_id
        )

        if origin_guild:

            member = origin_guild.get_member(
                applicant_id
            )

            if member:

                try:

                    await member.send(
                        f"🤝 **¡Tu alianza con {guild.name} fue aceptada!**\n\n"
                        f"Tu servidor **{server_name}** ya forma parte "
                        f"de las alianzas."
                    )

                except discord.Forbidden:
                    pass

    # ========================================================
    # RECHAZAR
    # ========================================================

    async def reject_alliance(
        self,
        interaction,
        origin_guild_id,
        applicant_id
    ):

        if not self.can_manage_alliance(
            interaction.user
        ):

            return await interaction.response.send_message(
                "❌ Necesitás **Gestionar servidor** para rechazar alianzas.",
                ephemeral=True
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
        # AVISAR AL SOLICITANTE
        # ====================================================

        origin_guild = self.bot.get_guild(
            origin_guild_id
        )

        if origin_guild:

            member = origin_guild.get_member(
                applicant_id
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

        guild_data = self.data.get(
            str(interaction.guild.id),
            {}
        )

        alliance_ids = guild_data.get(
            "alliances",
            []
        )

        if not alliance_ids:

            return await interaction.response.send_message(
                "🤝 **Todavía no tenemos alianzas oficiales.**",
                ephemeral=True
            )

        nombres = []

        for guild_id in alliance_ids:

            guild = self.bot.get_guild(
                int(guild_id)
            )

            if guild:

                nombres.append(
                    f"🤝 **{guild.name}**"
                )

        if not nombres:

            return await interaction.response.send_message(
                "🤝 No hay alianzas disponibles.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🤝 ALIANZAS OFICIALES",
            description="\n\n".join(nombres),
            color=PURPLE
        )

        embed.set_footer(
            text=f"{interaction.guild.name}"
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