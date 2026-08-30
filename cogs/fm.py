import os
import urllib.parse
import aiohttp
import discord
from discord.ext import commands

class FMCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_tokens = {}

    @commands.group(name="fm", invoke_without_command=True)
    async def fm(self, ctx):
        # Lógica del comando .fm
        pass

    @fm.command(name="login")
    async def login(self, ctx):
        # Lógica de .fm login
        pass

async def setup(bot):
    await bot.add_cog(FMCommand(bot))
