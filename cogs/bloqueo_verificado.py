import discord
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROL_VERIFICADO = "Verificado"

CANALES_BLOQUEADOS = {
    "🎸・𝙧𝙤𝙡𝙚𝙨",
    "𝙢𝙪𝙡𝙩𝙞𝙢𝙚𝙙𝙞𝙖・𝙧𝙤𝙡",
    "🔔・𝙖𝙣𝙪𝙣𝙘𝙞𝙤𝙨",
    "🎫・𝙩𝙞𝙘𝙠𝙚𝙩",
    "🗒️・𝙧𝙚𝙜𝙡𝙖𝙨",
    "・𝙞𝙣𝙫𝙞𝙩𝙖𝙘𝙞𝙤𝙣𝙚𝙨",
}

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)


# ============================================================
# COG
# ============================================================

class BloqueoVerificado(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print(
            "[VERIFICADO] Cog cargado correctamente."
        )

    # ========================================================
    # BUSCAR ROL
    # ========================================================

    def get_verified_role(self, guild):

        return discord.utils.get(
            guild.roles,
            name=ROL_VERIFICADO
        )

    # ========================================================
    # APLICAR BLOQUEO
    # ========================================================

    async def aplicar_bloqueo(self, guild):

        rol = self.get_verified_role(guild)

        if rol is None:
            return 0, 0

        encontrados = 0
        errores = 0

        for channel in guild.text_channels:

            if channel.name not in CANALES_BLOQUEADOS:
                continue

            try:

                await channel.set_permissions(
                    rol,
                    view_channel=True,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    add_reactions=True
                )

                encontrados += 1

            except discord.Forbidden:

                errores += 1

            except Exception as e:

                errores += 1

                print(
                    f"[VERIFICADO] Error en "
                    f"{channel.name}: {e}"
                )

        return encontrados, errores

    # ========================================================
    # QUITAR BLOQUEO
    # ========================================================

    async def quitar_bloqueo(self, guild):

        rol = self.get_verified_role(guild)

        if rol is None:
            return 0, 0

        encontrados = 0
        errores = 0

        for channel in guild.text_channels:

            if channel.name not in CANALES_BLOQUEADOS:
                continue

            try:

                # Elimina el override específico del rol
                await channel.set_permissions(
                    rol,
                    overwrite=None
                )

                encontrados += 1

            except discord.Forbidden:

                errores += 1

            except Exception as e:

                errores += 1

                print(
                    f"[VERIFICADO] Error quitando "
                    f"{channel.name}: {e}"
                )

        return encontrados, errores

    # ========================================================
    # BLOQUEAR VERIFICADO
    # ========================================================

    @commands.hybrid_command(
        name="bloquearverificado",
        description="Impide que Verificado escriba en los canales informativos."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def bloquearverificado(
        self,
        ctx
    ):

        encontrados, errores = await self.aplicar_bloqueo(
            ctx.guild
        )

        if encontrados == 0:

            await ctx.send(
                "❌ No encontré ninguno de los canales configurados "
                "o no encontré el rol **Verificado**."
            )

            return

        embed = discord.Embed(
            title="🔒・VERIFICADO BLOQUEADO",
            description=(
                f"El rol **Verificado** ya no puede escribir "
                f"en los canales configurados.\n\n"
                f"📁 **Canales modificados:** "
                f"**{encontrados}**\n"
                f"⚠️ **Errores:** **{errores}**"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text=f"Configurado por {ctx.author.display_name}"
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # DESBLOQUEAR VERIFICADO
    # ========================================================

    @commands.hybrid_command(
        name="desbloquearverificado",
        description="Quita el bloqueo de escritura de Verificado."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def desbloquearverificado(
        self,
        ctx
    ):

        encontrados, errores = await self.quitar_bloqueo(
            ctx.guild
        )

        if encontrados == 0:

            await ctx.send(
                "❌ No encontré ninguno de los canales configurados "
                "o no encontré el rol **Verificado**."
            )

            return

        embed = discord.Embed(
            title="🔓・VERIFICADO DESBLOQUEADO",
            description=(
                f"Se quitó el bloqueo específico del rol "
                f"**Verificado**.\n\n"
                f"📁 **Canales modificados:** "
                f"**{encontrados}**\n"
                f"⚠️ **Errores:** **{errores}**"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text=f"Configurado por {ctx.author.display_name}"
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # VERIFICAR ESTADO
    # ========================================================

    @commands.hybrid_command(
        name="estadoverificado",
        description="Muestra el estado del bloqueo de Verificado."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def estadoverificado(
        self,
        ctx
    ):

        rol = self.get_verified_role(
            ctx.guild
        )

        if rol is None:

            await ctx.send(
                "❌ No encontré el rol **Verificado**."
            )

            return

        bloqueados = []

        for channel in ctx.guild.text_channels:

            if channel.name not in CANALES_BLOQUEADOS:
                continue

            overwrite = channel.overwrites_for(
                rol
            )

            if overwrite.send_messages is False:

                bloqueados.append(
                    channel.name
                )

        embed = discord.Embed(
            title="🔎・ESTADO VERIFICADO",
            color=PURPLE
        )

        if bloqueados:

            embed.description = (
                "🔒 **Bloqueado en:**\n\n"
                + "\n".join(
                    f"• {channel}"
                    for channel in bloqueados
                )
            )

        else:

            embed.description = (
                "🔓 **Verificado no tiene bloqueado "
                "el envío de mensajes en los canales configurados.**"
            )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # ERRORES
    # ========================================================

    @bloquearverificado.error
    async def bloquear_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás **Administrador** para usar este comando."
            )

            return

        print(
            f"[VERIFICADO] Error: {error}"
        )

    @desbloquearverificado.error
    async def desbloquear_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás **Administrador** para usar este comando."
            )

            return

        print(
            f"[VERIFICADO] Error: {error}"
        )

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        print(
            "[VERIFICADO] Sistema listo."
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        BloqueoVerificado(bot)
    )