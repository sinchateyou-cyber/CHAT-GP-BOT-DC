import discord
from discord import app_commands
from discord.ext import commands


class PrivateChannel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="crearcanal",
        description="Crea un canal con acceso personalizado por roles."
    )
    @app_commands.describe(
        nombre="Nombre que tendrá el canal.",
        rol_permitido="El único rol que tendrá acceso al canal.",
        roles_bloqueados="Roles que no podrán acceder.",
        tipo="Tipo de canal."
    )
    @app_commands.choices(
        tipo=[
            app_commands.Choice(
                name="Texto",
                value="texto"
            ),
            app_commands.Choice(
                name="Voz",
                value="voz"
            )
        ]
    )
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def crearcanal(
        self,
        ctx: commands.Context,
        nombre: str,
        rol_permitido: discord.Role,
        roles_bloqueados: str = "",
        tipo: str = "texto"
    ):

        guild = ctx.guild
        bot_member = guild.me

        if bot_member is None:
            return await ctx.send(
                "❌ No pude encontrar al bot.",
                ephemeral=True
            )

        # --------------------------------------------------
        # PERMISOS DEL BOT
        # --------------------------------------------------

        if not bot_member.guild_permissions.manage_channels:
            return await ctx.send(
                "❌ Necesito el permiso **Gestionar canales**.",
                ephemeral=True
            )

        # --------------------------------------------------
        # COMPROBAR ROL PERMITIDO
        # --------------------------------------------------

        if rol_permitido.is_default():
            return await ctx.send(
                "❌ No podés utilizar `@everyone` como rol permitido.",
                ephemeral=True
            )

        if rol_permitido >= bot_member.top_role:
            return await ctx.send(
                "❌ El rol permitido está por encima de mi rol más alto.",
                ephemeral=True
            )

        # --------------------------------------------------
        # OBTENER ROLES BLOQUEADOS
        # --------------------------------------------------

        bloqueados = []

        if roles_bloqueados.strip():

            # Discord normalmente permite mencionar roles:
            # <@&123456789>
            partes = roles_bloqueados.split()

            for parte in partes:

                if parte.startswith("<@&") and parte.endswith(">"):

                    try:
                        role_id = int(
                            parte[3:-1]
                        )

                        role = guild.get_role(
                            role_id
                        )

                        if role and role not in bloqueados:
                            bloqueados.append(role)

                    except ValueError:
                        pass

        # --------------------------------------------------
        # NO PERMITIR BLOQUEAR EL ROL PRINCIPAL
        # --------------------------------------------------

        if rol_permitido in bloqueados:

            return await ctx.send(
                "❌ El rol permitido no puede estar "
                "también en los roles bloqueados.",
                ephemeral=True
            )

        # --------------------------------------------------
        # OVERWRITES
        # --------------------------------------------------

        overwrites = {

            # Nadie entra por defecto
            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            # Rol permitido
            rol_permitido:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    connect=True,
                    speak=True
                ),

            # Bot
            bot_member:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                    manage_messages=True,
                    connect=True,
                    speak=True
                )
        }

        # --------------------------------------------------
        # ROLES BLOQUEADOS
        # --------------------------------------------------

        for role in bloqueados:

            if role >= bot_member.top_role:
                continue

            overwrites[role] = discord.PermissionOverwrite(
                view_channel=False,
                send_messages=False,
                connect=False,
                speak=False
            )

        # --------------------------------------------------
        # CREAR CANAL
        # --------------------------------------------------

        try:

            if tipo == "voz":

                canal = await guild.create_voice_channel(
                    name=nombre,
                    overwrites=overwrites,
                    reason=(
                        f"Canal privado creado por "
                        f"{ctx.author}"
                    )
                )

            else:

                canal = await guild.create_text_channel(
                    name=nombre,
                    overwrites=overwrites,
                    reason=(
                        f"Canal privado creado por "
                        f"{ctx.author}"
                    )
                )

            # ------------------------------------------------
            # RESPUESTA
            # ------------------------------------------------

            embed = discord.Embed(
                title="🔐 Canal privado creado",
                description=(
                    f"Se creó correctamente {canal.mention}"
                ),
                color=discord.Color.blurple()
            )

            embed.add_field(
                name="👁️ Rol permitido",
                value=rol_permitido.mention,
                inline=False
            )

            if bloqueados:

                embed.add_field(
                    name="🚫 Roles bloqueados",
                    value="\n".join(
                        role.mention
                        for role in bloqueados
                    ),
                    inline=False
                )

            else:

                embed.add_field(
                    name="🚫 Roles bloqueados",
                    value="Ninguno",
                    inline=False
                )

            embed.set_footer(
                text=f"Creado por {ctx.author}"
            )

            await ctx.send(
                embed=embed,
                ephemeral=True
            )

        except discord.Forbidden:

            await ctx.send(
                "❌ No tengo permisos suficientes para "
                "crear o configurar el canal.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            await ctx.send(
                "❌ Discord rechazó la creación del canal.\n"
                f"`{error}`",
                ephemeral=True
            )


    # ======================================================
    # ERROR DEL COMANDO
    # ======================================================

    @crearcanal.error
    async def crearcanal_error(
        self,
        ctx: commands.Context,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás el permiso "
                "**Gestionar canales**.",
                ephemeral=True
            )

            return

        if isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                "❌ Revisá los roles y los parámetros "
                "que ingresaste.",
                ephemeral=True
            )

            return

        print(
            f"❌ Error en /crearcanal: {error}"
        )


async def setup(bot):
    await bot.add_cog(
        PrivateChannel(bot)
    )