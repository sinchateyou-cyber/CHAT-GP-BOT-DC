import json
from pathlib import Path
import discord
from discord.ext import commands
from discord import app_commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "reaction_roles.json"
# ============================================================
# DATOS
# ============================================================
def cargar_datos():
    DATA_FOLDER.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )
    try:
        data = json.loads(
            DATA_FILE.read_text(
                encoding="utf-8"
            )
        )
        if isinstance(data, dict):
            return data
        return {}
    except Exception as e:
        print(
            f"❌ Error leyendo reaction_roles.json: {e}"
        )
        return {}
def guardar_datos(data):
    DATA_FOLDER.mkdir(exist_ok=True)
    try:
        DATA_FILE.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )
    except Exception as e:
        print(
            f"❌ Error guardando reaction_roles.json: {e}"
        )
# ============================================================
# BOTÓN PERSISTENTE
# ============================================================
class RoleButton(discord.ui.Button):
    def __init__(
        self,
        role_id: int,
        panel_id: str
    ):
        self.role_id = role_id
        self.panel_id = panel_id
        super().__init__(
            label="Obtener rol",
            emoji="💜",
            style=discord.ButtonStyle.primary,
            # ==================================================
            # MUY IMPORTANTE
            # ==================================================
            # custom_id FIJO.
            #
            # Discord usa este ID para que el botón pueda
            # seguir funcionando después de reiniciar el bot.
            # ==================================================
            custom_id=f"reaction_role:{panel_id}"
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )
        # ====================================================
        # BUSCAR ROL
        # ====================================================
        role = interaction.guild.get_role(
            self.role_id
        )
        if role is None:
            return await interaction.response.send_message(
                "❌ No encontré el rol configurado.",
                ephemeral=True
            )
        # ====================================================
        # COMPROBAR USUARIO
        # ====================================================
        member = interaction.guild.get_member(
            interaction.user.id
        )
        if member is None:
            return await interaction.response.send_message(
                "❌ No pude encontrar tu usuario.",
                ephemeral=True
            )
        # ====================================================
        # COMPROBAR BOT
        # ====================================================
        me = interaction.guild.me
        if me is None:
            return await interaction.response.send_message(
                "❌ No pude comprobar los permisos del bot.",
                ephemeral=True
            )
        # ====================================================
        # JERARQUÍA
        # ====================================================
        if role >= me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo administrar ese rol porque está "
                "por encima de mi rol más alto.",
                ephemeral=True
            )
        # ====================================================
        # DAR / QUITAR ROL
        # ====================================================
        try:
            # ------------------------------------------------
            # SI YA TIENE EL ROL → QUITAR
            # ------------------------------------------------
            if role in member.roles:
                await member.remove_roles(
                    role,
                    reason="Reaction Role - quitar rol"
                )
                return await interaction.response.send_message(
                    f"❌ Te saqué el rol {role.mention}.",
                    ephemeral=True
                )
            # ------------------------------------------------
            # SI NO TIENE EL ROL → DAR
            # ------------------------------------------------
            await member.add_roles(
                role,
                reason="Reaction Role - obtener rol"
            )
            return await interaction.response.send_message(
                f"✅ Te asigné el rol {role.mention}.",
                ephemeral=True
            )
        except discord.Forbidden:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ No tengo permisos para administrar ese rol.",
                    ephemeral=True
                )
        except discord.HTTPException as e:
            print(
                f"❌ Error HTTP administrando rol "
                f"{self.role_id}: {e}"
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Discord rechazó la modificación del rol.",
                    ephemeral=True
                )
        except Exception as e:
            print(
                f"❌ Error administrando rol "
                f"{self.role_id}: {e}"
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al administrar el rol.",
                    ephemeral=True
                )
# ============================================================
# VIEW PERSISTENTE
# ============================================================
class RoleView(discord.ui.View):
    def __init__(
        self,
        role_id: int,
        panel_id: str
    ):
        # ====================================================
        # MUY IMPORTANTE
        # ====================================================
        # timeout=None = View persistente.
        # ====================================================
        super().__init__(
            timeout=None
        )
        self.add_item(
            RoleButton(
                role_id=role_id,
                panel_id=panel_id
            )
        )
# ============================================================
# COG
# ============================================================
class ReactionRoles(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
        self.data = cargar_datos()
    # ========================================================
    # CARGAR TODOS LOS PANELES AL INICIAR
    # ========================================================
    async def cog_load(self):
        cargados = 0
        errores = 0
        if not self.data:
            print(
                "ℹ️ No hay paneles de roles guardados."
            )
            return
        print(
            "🔄 Cargando paneles persistentes..."
        )
        # ====================================================
        # RECORRER TODOS LOS PANELES
        # ====================================================
        for panel_id, panel in self.data.items():
            try:
                # ------------------------------------------------
                # DATOS OBLIGATORIOS
                # ------------------------------------------------
                role_id = int(
                    panel["role_id"]
                )
                # ------------------------------------------------
                # REGISTRAR VIEW
                # ------------------------------------------------
                self.bot.add_view(
                    RoleView(
                        role_id=role_id,
                        panel_id=str(panel_id)
                    )
                )
                cargados += 1
                print(
                    f"   ✅ Panel {panel_id} "
                    f"(rol: {role_id})"
                )
            except KeyError as e:
                errores += 1
                print(
                    f"   ⚠️ Panel {panel_id} "
                    f"sin dato obligatorio: {e}"
                )
            except ValueError:
                errores += 1
                print(
                    f"   ⚠️ Panel {panel_id} "
                    f"tiene un ID inválido."
                )
            except Exception as e:
                errores += 1
                print(
                    f"   ❌ Error cargando panel "
                    f"{panel_id}: {e}"
                )
        # ====================================================
        # RESULTADO
        # ====================================================
        print(
            f"✅ Persistencia: {cargados} panel(es) "
            f"cargado(s), {errores} error(es)."
        )
    # ========================================================
    # /ROLPanel
    # ========================================================
    @app_commands.command(
        name="rolpanel",
        description=(
            "Crea un panel para obtener un rol mediante un botón."
        )
    )
    @app_commands.describe(
        rol="El rol que se entregará al tocar el botón.",
        titulo="Título del panel.",
        descripcion="Descripción del panel."
    )
    @app_commands.default_permissions(
        manage_roles=True
    )
    async def rolpanel(
        self,
        interaction: discord.Interaction,
        rol: discord.Role,
        titulo: str = "💜 Obtener rol",
        descripcion: str = (
            "Tocá el botón para obtener este rol."
        )
    ):
        # ====================================================
        # SERVIDOR
        # ====================================================
        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )
        # ====================================================
        # PERMISOS
        # ====================================================
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar roles**.",
                ephemeral=True
            )
        # ====================================================
        # JERARQUÍA
        # ====================================================
        me = interaction.guild.me
        if me is None:
            return await interaction.response.send_message(
                "❌ No pude comprobar la jerarquía del bot.",
                ephemeral=True
            )
        if me.top_role <= rol:
            return await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está "
                "por encima de mi rol más alto.",
                ephemeral=True
            )
        # ====================================================
        # ID ÚNICO DEL PANEL
        # ====================================================
        # Usamos el ID del mensaje como identificador único.
        # Discord lo generará cuando enviemos el mensaje.
        # Primero usamos un ID temporal único para el botón.
        # Después reemplazamos el registro persistente.
        # ====================================================
        import secrets
        panel_id = secrets.token_hex(
            8
        )
        # ====================================================
        # EMBED
        # ====================================================
        embed = discord.Embed(
            title=titulo,
            description=(
                f"{descripcion}\n\n"
                f"🎭 **Rol:** {rol.mention}\n\n"
                "**Tocá el botón de abajo para obtenerlo.**"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )
        embed.set_footer(
            text=interaction.guild.name
        )
        # ====================================================
        # VIEW
        # ====================================================
        view = RoleView(
            role_id=rol.id,
            panel_id=panel_id
        )
        # ====================================================
        # ENVIAR PANEL
        # ====================================================
        try:
            mensaje = await interaction.channel.send(
                embed=embed,
                view=view
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes "
                "o usar componentes en este canal.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            print(
                f"❌ Error HTTP enviando panel: {e}"
            )
            return await interaction.response.send_message(
                "❌ Discord rechazó la creación del panel.",
                ephemeral=True
            )
        except Exception as e:
            print(
                f"❌ Error enviando panel: {e}"
            )
            return await interaction.response.send_message(
                "❌ No pude crear el panel.",
                ephemeral=True
            )
        # ====================================================
        # GUARDAR
        # ====================================================
        self.data[str(panel_id)] = {
            "guild_id": interaction.guild.id,
            "channel_id": interaction.channel.id,
            "message_id": mensaje.id,
            "role_id": rol.id
        }
        guardar_datos(
            self.data
        )
        # ====================================================
        # RESPUESTA
        # ====================================================
        await interaction.response.send_message(
            "✅ Panel de roles creado correctamente.\n"
            "💾 Quedó guardado permanentemente y "
            "seguirá funcionando después de reiniciar el bot.",
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        ReactionRoles(bot)
    )