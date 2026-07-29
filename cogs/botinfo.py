import discord
from discord import app_commands
from discord.ext import commands


class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="botinfo",
        description="Muestra información sobre el bot y los servidores donde está."
    )
    async def botinfo(self, interaction: discord.Interaction):

        # Crear Embed
        embed = discord.Embed(
            title=f"🤖 Información de {self.bot.user.name}",
            description="Información general sobre mi bot.",
            color=discord.Color.blurple()
        )

        # Avatar del bot
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Cantidad de servidores
        embed.add_field(
            name="🌐 Servidores",
            value=f"`{len(self.bot.guilds)}`",
            inline=True
        )

        # Cantidad de usuarios
        total_users = sum(guild.member_count or 0 for guild in self.bot.guilds)

        embed.add_field(
            name="👥 Usuarios",
            value=f"`{total_users}`",
            inline=True
        )

        # Ping
        embed.add_field(
            name="📡 Ping",
            value=f"`{round(self.bot.latency * 1000)}ms`",
            inline=True
        )

        # Lista de servidores
        if self.bot.guilds:

            servidores = []

            for guild in self.bot.guilds:
                owner_text = "Desconocido"

                try:
                    if guild.owner:
                        owner_text = f"{guild.owner} (`{guild.owner.id}`)"
                except:
                    pass

                servidores.append(
                    f"**{guild.name}**\n"
                    f"🆔 ID: `{guild.id}`\n"
                    f"👑 Dueño: {owner_text}"
                )

            # Discord limita los embeds a 6000 caracteres
            texto = "\n\n".join(servidores)

            if len(texto) > 4000:
                texto = texto[:4000] + "\n\n... y más servidores."

            embed.add_field(
                name="🏠 Servidores donde estoy",
                value=texto,
                inline=False
            )

        embed.set_footer(
            text=f"Solicitado por {interaction.user}"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(BotInfo(bot))