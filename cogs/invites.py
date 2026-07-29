import discord
from discord.ext import commands
class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}
        self.invite_counts = {}
    async def cache_invites(self, guild):
        try:
            invites = await guild.invites()
            self.invite_cache[guild.id] = {
                invite.code: invite.uses or 0
                for invite in invites
            }
        except discord.Forbidden:
            print(
                f"No tengo permisos para ver invitaciones en "
                f"{guild.name}"
            )
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.cache_invites(guild)
        print("Invite Tracker iniciado.")
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.cache_invites(guild)
    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        try:
            invites = await guild.invites()
            old_invites = self.invite_cache.get(guild.id, {})
            used_invite = None
            for invite in invites:
                old_uses = old_invites.get(
                    invite.code,
                    0
                )
                new_uses = invite.uses or 0
                if new_uses > old_uses:
                    used_invite = invite
                    break
            self.invite_cache[guild.id] = {
                invite.code: invite.uses or 0
                for invite in invites
            }
            if used_invite is None:
                return
            inviter = used_invite.inviter
            if inviter is None:
                return
            if guild.id not in self.invite_counts:
                self.invite_counts[guild.id] = {}
            if inviter.id not in self.invite_counts[guild.id]:
                self.invite_counts[guild.id][inviter.id] = 0
            self.invite_counts[guild.id][inviter.id] += 1
            print(
                f"{inviter} invitó a {member} "
                f"en {guild.name}"
            )
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass
async def setup(bot):
    await bot.add_cog(InviteTracker(bot))