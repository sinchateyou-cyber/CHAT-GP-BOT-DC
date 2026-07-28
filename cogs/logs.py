import discord
from discord.ext import commands


class Logs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # BUSCAR CANAL DE LOGS
    # =========================

    def obtener_canal(self, guild):

        return discord.utils.get(
            guild.text_channels,
            name="logs"
        )

    # =========================
    # MENSAJE ELIMINADO
    # =========================

    @commands.Cog.listener()
    async def on_message_delete(self, mensaje):

        if mensaje.author.bot:
            return

        if not mensaje.guild:
            return

        canal = self.obtener_canal(
            mensaje.guild
        )

        if canal is None:
            return

        contenido = (
            mensaje.content
            if mensaje.content
            else "Sin texto"
        )

        embed = discord.Embed(
            title="🗑️ Mensaje eliminado",
            description=contenido[:4000]
        )

        embed.add_field(
            name="👤 Usuario",
            value=mensaje.author.mention,
            inline=True
        )

        embed.add_field(
            name="📍 Canal",
            value=mensaje.channel.mention,
            inline=True
        )

        embed.set_footer(
            text=f"ID del mensaje: {mensaje.id}"
        )

        await canal.send(
            embed=embed
        )

    # =========================
    # MENSAJE EDITADO
    # =========================

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        mensaje_anterior,
        mensaje_nuevo
    ):

        if mensaje_anterior.author.bot:
            return

        if not mensaje_anterior.guild:
            return

        if (
            mensaje_anterior.content
            == mensaje_nuevo.content
        ):
            return

        canal = self.obtener_canal(
            mensaje_anterior.guild
        )

        if canal is None:
            return

        antes = (
            mensaje_anterior.content
            or "Sin texto"
        )

        despues = (
            mensaje_nuevo.content
            or "Sin texto"
        )

        embed = discord.Embed(
            title="✏️ Mensaje editado"
        )

        embed.add_field(
            name="👤 Usuario",
            value=mensaje_anterior.author.mention,
            inline=False
        )

        embed.add_field(
            name="📍 Canal",
            value=mensaje_anterior.channel.mention,
            inline=False
        )

        embed.add_field(
            name="🔴 Antes",
            value=antes[:1000],
            inline=False
        )

        embed.add_field(
            name="🟢 Después",
            value=despues[:1000],
            inline=False
        )

        await canal.send(
            embed=embed
        )

    # =========================
    # MIEMBRO SALE
    # =========================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        miembro
    ):

        canal = self.obtener_canal(
            miembro.guild
        )

        if canal is None:
            return

        await canal.send(
            f"👋 **{miembro}** salió del servidor."
        )

    # =========================
    # MIEMBRO BANEADO
    # =========================

    @commands.Cog.listener()
    async def on_member_ban(
        self,
        guild,
        usuario
    ):

        canal = self.obtener_canal(
            guild
        )

        if canal is None:
            return

        await canal.send(
            f"🔨 **{usuario}** fue baneado."
        )

    # =========================
    # ERROR GENERAL
    # =========================

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.CommandNotFound
        ):
            return


async def setup(bot):
    await bot.add_cog(
        Logs(bot)
    )