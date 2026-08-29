import discord
from discord import app_commands
from discord.ext import commands

class VoiceActions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ============================================================
    # COMANDO: MUTEAR EN CANAL DE VOZ
    # ============================================================
    @app_commands.command(
        name="vmute",
        description="Mutea o desmutea a un miembro en un canal de voz."
    )
    @app_commands.describe(
        miembro="El miembro a mutear o desmutear en voz",
        estado="True para mutear, False para desmutear",
        razon="Razón del silenciamiento en voz"
    )
    @app_commands.default_permissions(mute_members=True)
    async def vmute(
        self, 
        interaction: discord.Interaction, 
        miembro: discord.Member, 
        estado: bool = True,
        razon: str = None
    ):
        await interaction.response.defer(ephemeral=True)

        if not miembro.voice or not miembro.voice.channel:
            await interaction.followup.send(
                f"❌ **{miembro.display_name}** no está conectado a ningún canal de voz.",
                ephemeral=True
            )
            return

        try:
            await miembro.edit(mute=estado, reason=razon or "Acción realizada por el bot")
            accion = "muteado" if estado else "desmuteado"
            await interaction.followup.send(
                f"✅ **{miembro.display_name}** ha sido **{accion}** del canal de voz.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos suficientes para modificar a este usuario.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error al intentar mutear en voz: `{e}`",
                ephemeral=True
            )

    # ============================================================
    # COMANDO: MOVER DE CANAL DE VOZ
    # ============================================================
    @app_commands.command(
        name="vmove",
        description="Mueve a un miembro de un canal de voz a otro."
    )
    @app_commands.describe(
        miembro="El miembro que deseas mover",
        canal_destino="El canal de voz al cual quieres moverlo",
        razon="Razón del movimiento"
    )
    @app_commands.default_permissions(move_members=True)
    async def vmove(
        self, 
        interaction: discord.Interaction, 
        miembro: discord.Member, 
        canal_destino: discord.VoiceChannel,
        razon: str = None
    ):
        await interaction.response.defer(ephemeral=True)

        if not miembro.voice or not miembro.voice.channel:
            await interaction.followup.send(
                f"❌ **{miembro.display_name}** no está conectado a ningún canal de voz.",
                ephemeral=True
            )
            return

        try:
            await miembro.move_to(canal_destino, reason=razon or "Acción realizada por el bot")
            await interaction.followup.send(
                f"✅ **{miembro.display_name}** movido a **{canal_destino.name}**.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos suficientes para mover a este usuario.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error al intentar mover en voz: `{e}`",
                ephemeral=True
            )

    # ============================================================
    # COMANDO: EXPULSAR DE CANAL DE VOZ (DISCONNECT)
    # ============================================================
    @app_commands.command(
        name="vkick",
        description="Expulsa (desconecta) a un miembro de su canal de voz."
    )
    @app_commands.describe(
        miembro="El miembro que deseas desconectar del canal de voz",
        razon="Razón de la desconexión"
    )
    @app_commands.default_permissions(move_members=True)
    async def vkick(
        self, 
        interaction: discord.Interaction, 
        miembro: discord.Member, 
        razon: str = None
    ):
        await interaction.response.defer(ephemeral=True)

        if not miembro.voice or not miembro.voice.channel:
            await interaction.followup.send(
                f"❌ **{miembro.display_name}** no está conectado a ningún canal de voz.",
                ephemeral=True
            )
            return

        try:
            # En discord.py, desconectar se logra moviendo al usuario a None
            await miembro.move_to(None, reason=razon or "Acción realizada por el bot")
            await interaction.followup.send(
                f"✅ **{miembro.display_name}** ha sido expulsado del canal de voz.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos suficientes para desconectar a este usuario.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error al intentar desconectar del canal de voz: `{e}`",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceActions(bot))
