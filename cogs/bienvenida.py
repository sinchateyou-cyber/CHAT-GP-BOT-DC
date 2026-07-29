import discord
from discord import app_commands
from discord.ext import commands
class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channels = {}
    @app_commands.command(
        name="setwelcome",
        description="Configura el canal de bienvenida"
    )
    @app_commands.describe(
        canal="Canal donde se enviarán las bienvenidas"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        self.welcome_channels[interaction.guild.id] = canal.id
        embed = discord.Embed(
            title="✅ Bienvenida configurada",
            description=(
                f"Los nuevos miembros recibirán su bienvenida en {canal.mention}."
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = self.welcome_channels.get(member.guild.id)
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return
        embed = discord.Embed(
            title="👋 ¡Bienvenido!",
            description=(
                f"¡Bienvenido/a {member.mention} a **{member.guild.name}**!\n\n"
                f"Ahora somos **{member.guild.member_count}** miembros."
            ),
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
async def setup(bot):
    await bot.add_cog(Welcome(bot))

Uso

/setwelcome canal:#bienvenidas

El bot guardará el canal y, cuando entre un nuevo miembro, enviará automáticamente el mensaje de bienvenida.

⚠️ Importante: esta versión guarda la configuración en memoria. Si reiniciás el bot, tendrás que volver a usar /setwelcome. Para que quede guardado permanentemente, habría que usar un archivo JSON o una base de datos.