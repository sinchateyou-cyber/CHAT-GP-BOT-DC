import discord
from discord.ext import commands


class AFK(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}

    @commands.command()
    async def afk(self, ctx, *, motivo="Sin motivo"):

        guild_id = ctx.guild.id
        user_id = ctx.author.id

        if guild_id not in self.afk_users:
            self.afk_users[guild_id] = {}

        self.afk_users[guild_id][user_id] = motivo

        await ctx.send(
            f"💤 {ctx.author.mention} ahora está AFK.\n"
            f"📝 Motivo: {motivo}"
        )

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not message.guild:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        # Quitar AFK cuando el usuario vuelve a escribir
        if guild_id in self.afk_users:

            if user_id in self.afk_users[guild_id]:

                del self.afk_users[guild_id][user_id]

                await message.channel.send(
                    f"👋 Bienvenido de vuelta "
                    f"{message.author.mention}, "
                    f"se quitó tu estado AFK."
                )

        # Avisar cuando mencionan a alguien AFK
        if guild_id in self.afk_users:

            for usuario in message.mentions:

                if usuario.id in self.afk_users[guild_id]:

                    motivo = self.afk_users[guild_id][usuario.id]

                    await message.channel.send(
                        f"💤 **{usuario.display_name}** "
                        f"está AFK.\n"
                        f"📝 Motivo: {motivo}"
                    )

        # MUY IMPORTANTE:
        # Permite que sigan funcionando !ping, !ban, !afk, etc.
        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(AFK(bot))