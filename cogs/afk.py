import discord
from discord.ext import commands
class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Guarda los usuarios AFK
        # Formato:
        # {user_id: "motivo"}
        self.afk_users = {}
    # =========================
    # COMANDO AFK
    # =========================
    @commands.command(name="afk")
    async def afk(self, ctx, *, motivo: str = None):
        # =========================
        # DESACTIVAR AFK
        # =========================
        if motivo and motivo.lower() == "off":
            if ctx.author.id not in self.afk_users:
                await ctx.send(
                    f"❌ {ctx.author.mention}, no estás en AFK."
                )
                return
            del self.afk_users[ctx.author.id]
            embed = discord.Embed(
                title="👋 AFK desactivado",
                description=(
                    f"Bienvenido de nuevo, {ctx.author.mention}."
                )
            )
            embed.set_thumbnail(
                url=ctx.author.display_avatar.url
            )
            await ctx.send(
                embed=embed
            )
            return
        # =========================
        # ACTIVAR AFK
        # =========================
        if ctx.author.id in self.afk_users:
            await ctx.send(
                f"💤 {ctx.author.mention}, ya estás en AFK.\n"
                f"Usá `!afk off` para desactivarlo."
            )
            return
        # Si no puso motivo
        if not motivo:
            motivo = "Sin motivo"
        self.afk_users[ctx.author.id] = motivo
        embed = discord.Embed(
            title="💤 AFK activado",
            description=(
                f"{ctx.author.mention} ahora está AFK."
            )
        )
        embed.add_field(
            name="📝 Motivo",
            value=motivo,
            inline=False
        )
        embed.set_thumbnail(
            url=ctx.author.display_avatar.url
        )
        embed.set_footer(
            text="Escribí !afk off para quitar tu AFK manualmente."
        )
        await ctx.send(
            embed=embed
        )
    # =========================
    # DETECTAR MENSAJES
    # =========================
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorar mensajes de bots
        if message.author.bot:
            return
        # =========================
        # QUITAR AFK AL HABLAR
        # =========================
        if message.author.id in self.afk_users:
            motivo = self.afk_users.pop(
                message.author.id
            )
            await message.channel.send(
                f"👋 Bienvenido de nuevo, "
                f"{message.author.mention}. "
                f"Tu AFK fue desactivado automáticamente."
            )
        # =========================
        # AVISAR SI MENCIONAN A UN AFK
        # =========================
        for usuario in message.mentions:
            if usuario.id in self.afk_users:
                motivo = self.afk_users[
                    usuario.id
                ]
                await message.channel.send(
                    f"💤 {usuario.mention} está AFK.\n"
                    f"📝 **Motivo:** {motivo}"
                )
        # =========================
        # IMPORTANTE
        # =========================
        # Como usamos on_message,
        # hay que procesar los comandos manualmente.
        await self.bot.process_commands(message)
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        AFK(bot)
    )