import discord
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

VERIFIED_ROLE_ID = 1536972961897119928

BLOCKED_CHANNEL_IDS = {
    1534290617486672034,  # 🎸・𝙧𝙤𝙡𝙚𝙨
    1536922172029800592,  # 𝙢𝙪𝙡𝙩𝙞𝙢𝙚𝙙𝙞𝙖・𝙧𝙤𝙡
    1534415451373834412,  # 🔔・𝙖𝙣𝙪𝙣𝙘𝙞𝙤𝙨
    1536210766238187530,  # 🎫・𝙩𝙞𝙘𝙠𝙚𝙩
    1534290827767971934,  # 🗒️・𝙧𝙚𝙜𝙡𝙖𝙨
    1536200070905724998,  # ・𝙞𝙣𝙫𝙞𝙩𝙖𝙘𝙞𝙤𝙣𝙚𝙨
}

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)


# ============================================================
# VERIFICATION COG
# ============================================================

class Verification(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "[VERIFICATION] Sistema cargado."
        )

    # ========================================================
    # OBTENER ROL
    # ========================================================

    def get_verified_role(
        self,
        guild
    ):

        return guild.get_role(
            VERIFIED_ROLE_ID
        )

    # ========================================================
    # APLICAR BLOQUEO
    # ========================================================

    async def apply_block(
        self,
        guild
    ):

        role = self.get_verified_role(
            guild
        )

        if role is None:

            print(
                f"[VERIFICATION] No encontré el rol "
                f"{VERIFIED_ROLE_ID} en {guild.name}"
            )

            return 0

        modified = 0

        for channel_id in BLOCKED_CHANNEL_IDS:

            channel = guild.get_channel(
                channel_id
            )

            if channel is None:
                continue

            try:

                await channel.set_permissions(
                    role,
                    view_channel=True,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    add_reactions=True
                )

                modified += 1

            except discord.Forbidden:

                print(
                    f"[VERIFICATION] Sin permisos en "
                    f"#{channel.name}"
                )

            except Exception as e:

                print(
                    f"[VERIFICATION] Error en "
                    f"#{channel.name}: {e}"
                )

        return modified

    # ========================================================
    # QUITAR BLOQUEO
    # ========================================================

    async def remove_block(
        self,
        guild
    ):

        role = self.get_verified_role(
            guild
        )

        if role is None:
            return 0

        modified = 0

        for channel_id in BLOCKED_CHANNEL_IDS:

            channel = guild.get_channel(
                channel_id
            )

            if channel is None:
                continue

            try:

                await channel.set_permissions(
                    role,
                    overwrite=None
                )

                modified += 1

            except Exception as e:

                print(
                    f"[VERIFICATION] Error quitando "
                    f"#{channel.name}: {e}"
                )

        return modified

    # ========================================================
    # BOTÓN DE VERIFICACIÓN
    # ========================================================

    async def verify_user(
        self,
        interaction
    ):

        guild = interaction.guild
        member = interaction.user

        if guild is None:

            await interaction.response.send_message(
                "❌ Este sistema solo funciona dentro del servidor.",
                ephemeral=True
            )

            return

        role = self.get_verified_role(
            guild
        )

        if role is None:

            await interaction.response.send_message(
                "❌ No encontré el rol **Verificado**.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Asegurar bloqueo
        # ----------------------------------------------------

        await self.apply_block(
            guild
        )

        # ----------------------------------------------------
        # Ya verificado
        # ----------------------------------------------------

        if role in member.roles:

            await interaction.response.send_message(
                "✅ Ya estás verificado.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Agregar rol
        # ----------------------------------------------------

        try:

            await member.add_roles(
                role,
                reason="Verificación mediante panel"
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para asignarte "
                "el rol **Verificado**.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # Confirmación
        # ----------------------------------------------------

        embed = discord.Embed(
            title="✅・VERIFICACIÓN COMPLETADA",
            description=(
                f"¡Listo, {member.mention}!\n\n"
                f"Recibiste el rol {role.mention}.\n\n"
                "Ya estás verificado correctamente."
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # PANEL
    # ========================================================

    @commands.hybrid_command(
        name="panelverificacion",
        description="Envía el panel de verificación."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def panelverificacion(
        self,
        ctx
    ):

        role = self.get_verified_role(
            ctx.guild
        )

        if role is None:

            await ctx.send(
                "❌ No encontré el rol **Verificado**."
            )

            return

        await self.apply_block(
            ctx.guild
        )

        embed = discord.Embed(
            title="💜・VERIFICACIÓN",
            description=(
                "### ¡Bienvenido/a!\n\n"
                "Para acceder correctamente al servidor "
                "tenés que verificarte.\n\n"
                "Presioná el botón de abajo:\n\n"
                "### ✅ Verificarme\n\n"
                "Una vez verificado recibirás "
                f"el rol {role.mention}."
            ),
            color=PURPLE
        )

        embed.set_footer(
            text="Sistema de verificación • Band Arg"
        )

        await ctx.send(
            embed=embed,
            view=VerificationView(
                self
            )
        )

    # ========================================================
    # VERIFICAR POR COMANDO
    # ========================================================

    @commands.hybrid_command(
        name="verificar",
        description="Te da el rol Verificado."
    )
    @commands.guild_only()
    async def verificar(
        self,
        ctx
    ):

        role = self.get_verified_role(
            ctx.guild
        )

        if role is None:

            await ctx.send(
                "❌ No encontré el rol **Verificado**."
            )

            return

        await self.apply_block(
            ctx.guild
        )

        if role in ctx.author.roles:

            await ctx.send(
                "✅ Ya estás verificado."
            )

            return

        try:

            await ctx.author.add_roles(
                role,
                reason="Verificación mediante comando"
            )

            await ctx.send(
                f"✅ {ctx.author.mention}, "
                "ya estás **verificado**."
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No tengo permisos para darte "
                "el rol **Verificado**."
            )

    # ========================================================
    # DESVERIFICAR
    # ========================================================

    @commands.hybrid_command(
        name="desverificar",
        description="Quita el rol Verificado."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def desverificar(
        self,
        ctx,
        usuario: discord.Member
    ):

        role = self.get_verified_role(
            ctx.guild
        )

        if role is None:

            await ctx.send(
                "❌ No encontré el rol **Verificado**."
            )

            return

        if role not in usuario.roles:

            await ctx.send(
                "❌ Ese usuario no está verificado."
            )

            return

        try:

            await usuario.remove_roles(
                role,
                reason="Desverificación administrativa"
            )

            await ctx.send(
                f"🔓 Se quitó el rol **Verificado** "
                f"a {usuario.mention}."
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No tengo permisos para quitar "
                "el rol."
            )

    # ========================================================
    # BLOQUEAR
    # ========================================================

    @commands.hybrid_command(
        name="bloquearverificado",
        description="Bloquea a Verificado en los canales configurados."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def bloquearverificado(
        self,
        ctx
    ):

        modified = await self.apply_block(
            ctx.guild
        )

        embed = discord.Embed(
            title="🔒・BLOQUEO ACTIVADO",
            description=(
                "El rol **Verificado** no puede escribir "
                "en los canales configurados.\n\n"
                f"📁 Canales modificados: **{modified}**"
            ),
            color=PURPLE
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # DESBLOQUEAR
    # ========================================================

    @commands.hybrid_command(
        name="desbloquearverificado",
        description="Desbloquea a Verificado."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def desbloquearverificado(
        self,
        ctx
    ):

        modified = await self.remove_block(
            ctx.guild
        )

        embed = discord.Embed(
            title="🔓・BLOQUEO DESACTIVADO",
            description=(
                "Se quitó el bloqueo específico "
                "del rol **Verificado**.\n\n"
                f"📁 Canales modificados: **{modified}**"
            ),
            color=PURPLE
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # ESTADO
    # ========================================================

    @commands.hybrid_command(
        name="estadoverificado",
        description="Muestra el estado del bloqueo."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def estadoverificado(
        self,
        ctx
    ):

        role = self.get_verified_role(
            ctx.guild
        )

        if role is None:

            await ctx.send(
                "❌ No encontré el rol **Verificado**."
            )

            return

        blocked = []

        for channel_id in BLOCKED_CHANNEL_IDS:

            channel = ctx.guild.get_channel(
                channel_id
            )

            if channel is None:
                continue

            overwrite = channel.overwrites_for(
                role
            )

            if overwrite.send_messages is False:

                blocked.append(
                    channel.mention
                )

        if blocked:

            description = (
                "🔒 **Verificado está bloqueado en:**\n\n"
                + "\n".join(blocked)
            )

        else:

            description = (
                "🔓 **Verificado no está bloqueado "
                "en los canales configurados.**"
            )

        embed = discord.Embed(
            title="🔎・ESTADO VERIFICADO",
            description=description,
            color=PURPLE
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        print(
            "[VERIFICATION] Aplicando bloqueos..."
        )

        for guild in self.bot.guilds:

            try:

                await self.apply_block(
                    guild
                )

            except Exception as e:

                print(
                    f"[VERIFICATION] Error en "
                    f"{guild.name}: {e}"
                )

        print(
            "[VERIFICATION] Sistema listo."
        )


# ============================================================
# VIEW PERSISTENTE
# ============================================================

class VerificationView(
    discord.ui.View
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            VerificationButton(
                cog
            )
        )


# ============================================================
# BOTÓN PERSISTENTE
# ============================================================

class VerificationButton(
    discord.ui.Button
):

    def __init__(
        self,
        cog
    ):

        super().__init__(
            label="Verificarme",
            emoji="✅",
            style=discord.ButtonStyle.success,
            custom_id="verification:verify"
        )

        self.cog = cog

    async def callback(
        self,
        interaction
    ):

        await self.cog.verify_user(
            interaction
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    cog = Verification(
        bot
    )

    await bot.add_cog(
        cog
    )

    # --------------------------------------------------------
    # Registrar View persistente
    # --------------------------------------------------------

    bot.add_view(
        VerificationView(
            cog
        )
    )

    print(
        "[VERIFICATION] View persistente registrada."
    )