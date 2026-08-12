import discord
from discord.ext import commands
from discord import app_commands


CANAL_NOMBRE = "╭・𝐌𝐞𝐝𝐢𝐚 𝐑𝐨𝐥・🎞️"

ROLES = {
    "🖼️": "𝐌𝐞𝐝𝐢𝐚・𝐈𝐦𝐚́𝐠𝐞𝐧𝐞𝐬",
    "🎞️": "𝐌𝐞𝐝𝐢𝐚・𝐆𝐈𝐅𝐬",
    "📹": "𝐌𝐞𝐝𝐢𝐚・𝐕𝐢́𝐝𝐞𝐨𝐬",
    "📎": "𝐌𝐞𝐝𝐢𝐚・𝐀𝐫𝐜𝐡𝐢𝐯𝐨𝐬",
}


class MediaRoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def toggle_role(
        self,
        interaction: discord.Interaction,
        role_name: str
    ):

        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "❌ Este sistema solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return

        role = discord.utils.get(
            guild.roles,
            name=role_name
        )

        if role is None:
            await interaction.response.send_message(
                "❌ El rol no existe.",
                ephemeral=True
            )
            return

        member = interaction.user

        me = guild.me

        if me is None or role >= me.top_role:
            await interaction.response.send_message(
                "❌ No puedo administrar ese rol porque está por encima "
                "o al mismo nivel que mi rol más alto.",
                ephemeral=True
            )
            return

        try:

            if role in member.roles:

                await member.remove_roles(
                    role,
                    reason="Media Role - quitar rol"
                )

                await interaction.response.send_message(
                    f"❌ Te saqué el rol {role.mention}.",
                    ephemeral=True
                )

            else:

                await member.add_roles(
                    role,
                    reason="Media Role - asignar rol"
                )

                await interaction.response.send_message(
                    f"✅ Te di el rol {role.mention}.",
                    ephemeral=True
                )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para modificar ese rol.",
                ephemeral=True
            )

        except discord.HTTPException:

            await interaction.response.send_message(
                "❌ Discord rechazó la modificación del rol.",
                ephemeral=True
            )

    @discord.ui.button(
        label="Imágenes",
        emoji="🖼️",
        style=discord.ButtonStyle.secondary,
        custom_id="media_role:imagenes"
    )
    async def imagenes(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.toggle_role(
            interaction,
            ROLES["🖼️"]
        )

    @discord.ui.button(
        label="GIFs",
        emoji="🎞️",
        style=discord.ButtonStyle.secondary,
        custom_id="media_role:gifs"
    )
    async def gifs(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.toggle_role(
            interaction,
            ROLES["🎞️"]
        )

    @discord.ui.button(
        label="Videos",
        emoji="📹",
        style=discord.ButtonStyle.secondary,
        custom_id="media_role:videos"
    )
    async def videos(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.toggle_role(
            interaction,
            ROLES["📹"]
        )

    @discord.ui.button(
        label="Archivos",
        emoji="📎",
        style=discord.ButtonStyle.secondary,
        custom_id="media_role:archivos"
    )
    async def archivos(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.toggle_role(
            interaction,
            ROLES["📎"]
        )


class MediaRol(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="crear-media-rol",
        description="Crea el canal y panel de roles multimedia."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def crear_media_rol(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

            return

        await interaction.response.defer(
            ephemeral=True
        )

        # ====================================================
        # CREAR ROLES
        # ====================================================

        roles_creados = {}

        for emoji, nombre in ROLES.items():

            role = discord.utils.get(
                guild.roles,
                name=nombre
            )

            if role is None:

                try:

                    role = await guild.create_role(
                        name=nombre,
                        reason="Sistema de roles multimedia"
                    )

                except discord.Forbidden:

                    await interaction.followup.send(
                        "❌ No tengo permiso para crear roles.",
                        ephemeral=True
                    )

                    return

            roles_creados[emoji] = role

        # ====================================================
        # BUSCAR / CREAR CANAL
        # ====================================================

        canal = discord.utils.get(
            guild.text_channels,
            name=CANAL_NOMBRE
        )

        if canal is None:

            try:

                canal = await guild.create_text_channel(
                    CANAL_NOMBRE,
                    reason="Sistema de roles multimedia"
                )

            except discord.Forbidden:

                await interaction.followup.send(
                    "❌ No tengo permiso para crear canales.",
                    ephemeral=True
                )

                return

        # ====================================================
        # PERMISOS
        # ====================================================

        overwrites = {}

        overwrites[guild.default_role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=False,
            attach_files=False,
            embed_links=False
        )

        bot_member = guild.me

        if bot_member:

            overwrites[bot_member] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
                manage_messages=True
            )

        for role in roles_creados.values():

            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            )

        try:

            await canal.edit(
                overwrites=overwrites
            )

        except discord.Forbidden:
            pass

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="🎞️ ROLES MULTIMEDIA",
            description=(
                "**Elegí el rol que corresponda según "
                "el contenido multimedia que quieras enviar.**\n\n"
                "**🖼️ Imágenes** — Podés enviar imágenes.\n\n"
                "**🎞️ GIFs** — Podés enviar GIFs.\n\n"
                "**📹 Videos** — Podés enviar videos.\n\n"
                "**📎 Archivos** — Podés enviar archivos.\n\n"
                "**Seleccioná tu rol abajo para obtener acceso.**"
            ),
            color=discord.Color.from_rgb(
                145,
                70,
                255
            )
        )

        embed.set_footer(
            text="Seleccioná nuevamente el botón para quitarte el rol."
        )

        # ====================================================
        # PANEL
        # ====================================================

        try:

            await canal.send(
                embed=embed,
                view=MediaRoleView()
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ No puedo enviar mensajes en ese canal.",
                ephemeral=True
            )

            return

        await interaction.followup.send(
            f"✅ **Sistema creado correctamente.**\n\n"
            f"📁 Canal: {canal.mention}\n"
            f"🖼️ {roles_creados['🖼️'].mention}\n"
            f"🎞️ {roles_creados['🎞️'].mention}\n"
            f"📹 {roles_creados['📹'].mention}\n"
            f"📎 {roles_creados['📎'].mention}",
            ephemeral=True
        )


async def setup(bot):

    await bot.add_cog(
        MediaRol(bot)
    )