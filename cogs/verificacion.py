import discord
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
# ID DEL ROL VERIFICADO
ROL_VERIFICADO_ID = 1531610712244490391
# ============================================================
# VISTA DEL BOTÓN DE VERIFICACIÓN
# ============================================================
class VerificacionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(
        label="Verificarme",
        emoji="✅",
        style=discord.ButtonStyle.green,
        custom_id="boton_verificar"
    )
    async def verificar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        # Comprobar servidor
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return
        guild = interaction.guild
        usuario = interaction.user
        # ====================================================
        # BUSCAR ROL POR ID
        # ====================================================
        rol = guild.get_role(
            ROL_VERIFICADO_ID
        )
        # ====================================================
        # SI NO EXISTE EL ROL
        # ====================================================
        if rol is None:
            await interaction.response.send_message(
                "❌ No pude encontrar el rol de verificación.\n\n"
                f"🆔 ID configurado: `{ROL_VERIFICADO_ID}`\n\n"
                "Comprobá que el ID corresponda a un rol de "
                "este servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR SI EL USUARIO YA TIENE EL ROL
        # ====================================================
        if rol in usuario.roles:
            await interaction.response.send_message(
                "ℹ️ Ya estás verificado.",
                ephemeral=True
            )
            return
        # ====================================================
        # OBTENER EL ROL MÁS ALTO DEL BOT
        # ====================================================
        bot_member = guild.me
        if bot_member is None:
            await interaction.response.send_message(
                "❌ No pude obtener la información del bot "
                "en este servidor.",
                ephemeral=True
            )
            return
        bot_top_role = bot_member.top_role
        # ====================================================
        # COMPROBAR JERARQUÍA DE ROLES
        # ====================================================
        if rol >= bot_top_role:
            await interaction.response.send_message(
                "❌ No puedo asignarte el rol de verificación.\n\n"
                "El rol del bot debe estar **por encima** del "
                "rol que intenta asignar.\n\n"
                f"🎭 Rol: {rol.mention}\n"
                f"🤖 Mi rol más alto: {bot_top_role.mention}\n\n"
                "Mové el rol del bot por encima del rol "
                "Verificado en **Configuración del servidor → Roles**.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR PERMISO MANAGE_ROLES
        # ====================================================
        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "❌ No tengo el permiso **Gestionar roles**.\n\n"
                "Dale al bot el permiso `Gestionar roles` "
                "para poder verificar usuarios.",
                ephemeral=True
            )
            return
        # ====================================================
        # ASIGNAR ROL
        # ====================================================
        try:
            await usuario.add_roles(
                rol,
                reason="Verificación mediante botón"
            )
            await interaction.response.send_message(
                "✅ ¡Te verificaste correctamente!\n"
                f"Ahora tenés el rol {rol.mention}.",
                ephemeral=True
            )
        # ====================================================
        # ERROR DE PERMISOS
        # ====================================================
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord rechazó la asignación del rol.\n\n"
                "Comprobá que el bot tenga el permiso "
                "**Gestionar roles** y que su rol esté por encima "
                "del rol Verificado.",
                ephemeral=True
            )
        # ====================================================
        # OTRO ERROR
        # ====================================================
        except discord.HTTPException as error:
            print(
                f"❌ Error de Discord al asignar el rol: {error}"
            )
            await interaction.response.send_message(
                "❌ Ocurrió un error de Discord al intentar "
                "asignarte el rol. Intentá nuevamente.",
                ephemeral=True
            )
# ============================================================
# COG DE VERIFICACIÓN
# ============================================================
class Verificacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ========================================================
    # COMANDO !VERIFICION
    # ========================================================
    @commands.command(
        name="verify"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def verificacion(
        self,
        ctx
    ):
        embed = discord.Embed(
            title="🛡️ Verificación",
            description=(
                "¡Bienvenido/a al servidor! 👋\n\n"
                "Para acceder al servidor, presioná el botón "
                "**Verificarme** de abajo.\n\n"
                "✅ Recibirás automáticamente el rol "
                "**Verificado**.\n\n"
                "🔒 Al verificarte, podrás acceder a los "
                "canales del servidor."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(
            text="Sistema de verificación"
        )
        await ctx.send(
            embed=embed,
            view=VerificacionView()
        )
    # ========================================================
    # ERROR DEL COMANDO
    # ========================================================
    @verificacion.error
    async def error_verificacion(
        self,
        ctx,
        error
    ):
        if isinstance(
            error,
            commands.MissingPermissions
        ):
            await ctx.send(
                "❌ Solo los administradores pueden "
                "crear el panel de verificación."
            )
        else:
            print(
                f"❌ Error en el comando de verificación: {error}"
            )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Verificacion(bot)
    )
    # ========================================================
    # REGISTRAR BOTÓN PERSISTENTE
    # ========================================================
    bot.add_view(
        VerificacionView()
    )