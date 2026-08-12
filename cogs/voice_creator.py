import discord
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

CREATE_CHANNEL_NAME = "➕・𝐂𝐫𝐞𝐚𝐫 𝐬𝐚𝐥𝐚"
CATEGORY_NAME = "╭・𝐕𝐨𝐳・🔊"
VOICE_PREFIX = "🔊・"


# ============================================================
# DATOS EN MEMORIA
# ============================================================

# channel_id -> owner_id
TEMP_CHANNELS = {}

# channel_id -> panel_message_id
PANEL_MESSAGES = {}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def is_voice_owner(channel_id, user_id):
    return TEMP_CHANNELS.get(channel_id) == user_id


def get_temp_channel(channel_id):
    return channel_id in TEMP_CHANNELS


# ============================================================
# MODAL: CAMBIAR NOMBRE
# ============================================================

class RenameVoiceModal(discord.ui.Modal, title="Cambiar nombre del voice"):

    nombre = discord.ui.TextInput(
        label="Nuevo nombre",
        placeholder="Ej: sala de Valentin",
        max_length=80,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.user.voice.channel

        if channel is None:
            await interaction.response.send_message(
                "❌ No estás dentro de tu voice.",
                ephemeral=True
            )
            return

        if not is_voice_owner(
            channel.id,
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Este voice no es tuyo.",
                ephemeral=True
            )
            return

        nuevo_nombre = str(self.nombre.value).strip()

        if not nuevo_nombre:
            await interaction.response.send_message(
                "❌ Escribí un nombre válido.",
                ephemeral=True
            )
            return

        if not nuevo_nombre.startswith(VOICE_PREFIX):
            nuevo_nombre = f"{VOICE_PREFIX}{nuevo_nombre}"

        try:
            await channel.edit(
                name=nuevo_nombre,
                reason="El dueño cambió el nombre de su voice"
            )

            await interaction.response.send_message(
                f"✅ Nombre cambiado a **{nuevo_nombre}**.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para cambiar el nombre.",
                ephemeral=True
            )


# ============================================================
# MODAL: LÍMITE DE USUARIOS
# ============================================================

class LimitVoiceModal(discord.ui.Modal, title="Límite de usuarios"):

    limite = discord.ui.TextInput(
        label="Cantidad de usuarios",
        placeholder="Ej: 5 — poné 0 para quitar el límite",
        max_length=2,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.user.voice.channel

        if channel is None:
            await interaction.response.send_message(
                "❌ No estás dentro de tu voice.",
                ephemeral=True
            )
            return

        if not is_voice_owner(
            channel.id,
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Este voice no es tuyo.",
                ephemeral=True
            )
            return

        try:
            limite = int(str(self.limite.value).strip())

        except ValueError:
            await interaction.response.send_message(
                "❌ Tenés que poner un número.",
                ephemeral=True
            )
            return

        if limite < 0 or limite > 99:
            await interaction.response.send_message(
                "❌ El límite tiene que estar entre **0 y 99**.",
                ephemeral=True
            )
            return

        try:
            await channel.edit(
                user_limit=limite,
                reason="El dueño cambió el límite del voice"
            )

            if limite == 0:
                mensaje = "✅ Se quitó el límite de usuarios."
            else:
                mensaje = (
                    f"✅ Límite cambiado a **{limite} usuarios**."
                )

            await interaction.response.send_message(
                mensaje,
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para cambiar el límite.",
                ephemeral=True
            )


# ============================================================
# PANEL DEL VOICE
# ============================================================

class VoicePanel(discord.ui.View):

    def __init__(self, channel_id):
        super().__init__(timeout=None)

        self.channel_id = channel_id

    async def get_channel(self, interaction):

        channel = interaction.guild.get_channel(
            self.channel_id
        )

        if channel is None:
            await interaction.response.send_message(
                "❌ Este voice ya no existe.",
                ephemeral=True
            )
            return None

        if not is_voice_owner(
            self.channel_id,
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Solo el dueño de este voice puede usar el panel.",
                ephemeral=True
            )
            return None

        return channel

    # ========================================================
    # CAMBIAR NOMBRE
    # ========================================================

    @discord.ui.button(
        label="Nombre",
        emoji="✏️",
        style=discord.ButtonStyle.primary,
        custom_id="voice_name"
    )
    async def name_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = await self.get_channel(interaction)

        if channel is None:
            return

        await interaction.response.send_modal(
            RenameVoiceModal()
        )

    # ========================================================
    # PRIVACIDAD
    # ========================================================

    @discord.ui.button(
        label="Privacidad",
        emoji="🔒",
        style=discord.ButtonStyle.secondary,
        custom_id="voice_privacy"
    )
    async def privacy_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = await self.get_channel(interaction)

        if channel is None:
            return

        await interaction.response.send_message(
            "🔐 Elegí la privacidad de tu voice:",
            view=PrivacyView(self.channel_id),
            ephemeral=True
        )

    # ========================================================
    # LÍMITE
    # ========================================================

    @discord.ui.button(
        label="Límite",
        emoji="👥",
        style=discord.ButtonStyle.secondary,
        custom_id="voice_limit"
    )
    async def limit_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = await self.get_channel(interaction)

        if channel is None:
            return

        await interaction.response.send_modal(
            LimitVoiceModal()
        )

    # ========================================================
    # BLOQUEAR
    # ========================================================

    @discord.ui.button(
        label="Bloquear",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="voice_lock"
    )
    async def lock_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = await self.get_channel(interaction)

        if channel is None:
            return

        try:
            await channel.set_permissions(
                interaction.guild.default_role,
                connect=False,
                reason="Voice bloqueado por su dueño"
            )

            await interaction.response.send_message(
                "🔒 Tu voice fue **bloqueado**.\n"
                "Solo las personas que ya están dentro pueden permanecer.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para bloquear el voice.",
                ephemeral=True
            )

    # ========================================================
    # ELIMINAR
    # ========================================================

    @discord.ui.button(
        label="Eliminar",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="voice_delete"
    )
    async def delete_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = await self.get_channel(interaction)

        if channel is None:
            return

        await interaction.response.send_message(
            "⚠️ ¿Seguro que querés eliminar tu voice?",
            view=DeleteConfirmView(self.channel_id),
            ephemeral=True
        )


# ============================================================
# PRIVACIDAD
# ============================================================

class PrivacyView(discord.ui.View):

    def __init__(self, channel_id):
        super().__init__(timeout=60)

        self.channel_id = channel_id

    async def check_owner(self, interaction):

        if not is_voice_owner(
            self.channel_id,
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Solo el dueño puede hacer esto.",
                ephemeral=True
            )
            return False

        return True

    # ========================================================
    # PÚBLICO
    # ========================================================

    @discord.ui.button(
        label="Público",
        emoji="🌎",
        style=discord.ButtonStyle.success
    )
    async def public_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.check_owner(interaction):
            return

        channel = interaction.guild.get_channel(
            self.channel_id
        )

        if channel is None:
            await interaction.response.send_message(
                "❌ El voice ya no existe.",
                ephemeral=True
            )
            return

        try:
            await channel.set_permissions(
                interaction.guild.default_role,
                connect=True,
                reason="Voice configurado como público"
            )

            await interaction.response.send_message(
                "🌎 Tu voice ahora es **público**.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para cambiar la privacidad.",
                ephemeral=True
            )

    # ========================================================
    # PRIVADO
    # ========================================================

    @discord.ui.button(
        label="Privado",
        emoji="🔐",
        style=discord.ButtonStyle.danger
    )
    async def private_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not await self.check_owner(interaction):
            return

        channel = interaction.guild.get_channel(
            self.channel_id
        )

        if channel is None:
            await interaction.response.send_message(
                "❌ El voice ya no existe.",
                ephemeral=True
            )
            return

        try:
            await channel.set_permissions(
                interaction.guild.default_role,
                connect=False,
                reason="Voice configurado como privado"
            )

            await channel.set_permissions(
                interaction.user,
                connect=True,
                speak=True,
                stream=True,
                use_voice_activation=True,
                reason="Permiso para el dueño del voice"
            )

            await interaction.response.send_message(
                "🔐 Tu voice ahora es **privado**.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para cambiar la privacidad.",
                ephemeral=True
            )


# ============================================================
# CONFIRMAR ELIMINACIÓN
# ============================================================

class DeleteConfirmView(discord.ui.View):

    def __init__(self, channel_id):
        super().__init__(timeout=30)

        self.channel_id = channel_id

    @discord.ui.button(
        label="Sí, eliminar",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not is_voice_owner(
            self.channel_id,
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Solo el dueño puede eliminar este voice.",
                ephemeral=True
            )
            return

        channel = interaction.guild.get_channel(
            self.channel_id
        )

        if channel is None:
            TEMP_CHANNELS.pop(
                self.channel_id,
                None
            )

            await interaction.response.send_message(
                "❌ El voice ya no existe.",
                ephemeral=True
            )
            return

        TEMP_CHANNELS.pop(
            self.channel_id,
            None
        )

        PANEL_MESSAGES.pop(
            self.channel_id,
            None
        )

        try:
            await channel.delete(
                reason="El dueño eliminó su voice"
            )

            await interaction.response.edit_message(
                content="🗑️ Tu voice fue eliminado.",
                view=None
            )

        except discord.Forbidden:
            TEMP_CHANNELS[self.channel_id] = interaction.user.id

            await interaction.response.send_message(
                "❌ No tengo permisos para eliminar el voice.",
                ephemeral=True
            )

    @discord.ui.button(
        label="Cancelar",
        emoji="❌",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            content="❌ Eliminación cancelada.",
            view=None
        )


# ============================================================
# COG PRINCIPAL
# ============================================================

class VoiceCreator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        print("✅ Voice Creator cargado correctamente.")

        # Registrar el canal creador en los servidores
        for guild in self.bot.guilds:
            try:
                await self.create_creator_channel(guild)

            except Exception as e:
                print(
                    f"❌ Error configurando voice en "
                    f"{guild.name}: {e}"
                )

    # ========================================================
    # CREAR CATEGORÍA
    # ========================================================

    async def get_category(self, guild):

        category = discord.utils.get(
            guild.categories,
            name=CATEGORY_NAME
        )

        if category is None:

            category = await guild.create_category(
                CATEGORY_NAME,
                reason="Sistema de voices temporales"
            )

        return category

    # ========================================================
    # CREAR CANAL CREADOR
    # ========================================================

    async def create_creator_channel(self, guild):

        category = await self.get_category(guild)

        creator = discord.utils.get(
            category.voice_channels,
            name=CREATE_CHANNEL_NAME
        )

        if creator is None:

            creator = await guild.create_voice_channel(
                CREATE_CHANNEL_NAME,
                category=category,
                reason="Canal creador de voices"
            )

        return creator

    # ========================================================
    # ENTRAR / SALIR DE VOICE
    # ========================================================

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):

        # ====================================================
        # ENTRÓ AL CANAL CREADOR
        # ====================================================

        if after.channel is not None:

            creator = discord.utils.get(
                after.channel.guild.voice_channels,
                name=CREATE_CHANNEL_NAME
            )

            if (
                creator is not None
                and after.channel.id == creator.id
            ):

                guild = member.guild
                category = after.channel.category

                # Nombre inicial
                channel_name = (
                    f"{VOICE_PREFIX}"
                    f"{member.display_name}"
                )

                try:

                    new_channel = (
                        await guild.create_voice_channel(
                            channel_name,
                            category=category,
                            reason=(
                                f"Voice temporal de "
                                f"{member}"
                            )
                        )
                    )

                    # Guardar dueño
                    TEMP_CHANNELS[
                        new_channel.id
                    ] = member.id

                    # Permisos públicos inicialmente
                    await new_channel.set_permissions(
                        guild.default_role,
                        connect=True,
                        speak=True,
                        stream=True,
                        use_voice_activation=True
                    )

                    # Permisos del dueño
                    await new_channel.set_permissions(
                        member,
                        connect=True,
                        speak=True,
                        stream=True,
                        use_voice_activation=True,
                        manage_channels=True,
                        move_members=True,
                        mute_members=True,
                        deafen_members=True
                    )

                    # Mover usuario
                    try:
                        await member.move_to(
                            new_channel,
                            reason="Entrar a su voice temporal"
                        )

                    except discord.Forbidden:
                        print(
                            f"⚠️ No pude mover a "
                            f"{member} al voice."
                        )

                    # ========================================
                    # ENVIAR PANEL
                    # ========================================

                    embed = discord.Embed(
                        title="🎛️・Panel de tu voice",
                        description=(
                            f"Bienvenido a **{new_channel.name}**.\n\n"
                            "Usá los botones de abajo para "
                            "administrar tu sala.\n\n"
                            "✏️ **Nombre**\n"
                            "Cambiar el nombre del voice.\n\n"
                            "🔒 **Privacidad**\n"
                            "Elegir entre público o privado.\n\n"
                            "👥 **Límite**\n"
                            "Cambiar la cantidad máxima de usuarios.\n\n"
                            "🔒 **Bloquear**\n"
                            "Bloquear nuevas entradas.\n\n"
                            "🗑️ **Eliminar**\n"
                            "Eliminar tu sala."
                        ),
                        color=discord.Color.blurple()
                    )

                    embed.set_footer(
                        text="Solo el dueño puede utilizar este panel."
                    )

                    panel_message = await new_channel.send(
                        embed=embed,
                        view=VoicePanel(new_channel.id)
                    )

                    PANEL_MESSAGES[
                        new_channel.id
                    ] = panel_message.id

                    print(
                        f"🔊 Voice creado: "
                        f"{new_channel.name} | "
                        f"Dueño: {member}"
                    )

                except discord.Forbidden:

                    print(
                        "❌ El bot no tiene permisos "
                        "para crear canales de voz."
                    )

                except Exception as e:

                    print(
                        f"❌ Error creando voice: {e}"
                    )

        # ====================================================
        # SALIÓ DE UN CANAL
        # ====================================================

        if before.channel is not None:

            channel = before.channel

            # No es un canal temporal
            if channel.id not in TEMP_CHANNELS:
                return

            # Todavía hay gente
            if len(channel.members) > 0:
                return

            # Eliminar automáticamente
            try:

                TEMP_CHANNELS.pop(
                    channel.id,
                    None
                )

                PANEL_MESSAGES.pop(
                    channel.id,
                    None
                )

                await channel.delete(
                    reason="Voice temporal vacío"
                )

                print(
                    f"🗑️ Voice eliminado: "
                    f"{channel.name}"
                )

            except discord.NotFound:

                TEMP_CHANNELS.pop(
                    channel.id,
                    None
                )

            except discord.Forbidden:

                print(
                    f"❌ No puedo eliminar "
                    f"{channel.name}."
                )

            except Exception as e:

                print(
                    f"❌ Error eliminando voice: {e}"
                )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(VoiceCreator(bot))