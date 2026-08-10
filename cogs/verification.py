import discord
from discord.ext import commands
import json
import os

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "verification.json")

os.makedirs(DATA_FOLDER, exist_ok=True)


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(DATA_FILE):
            data = {
                "message_id": None,
                "channel_id": None,
                "role_id": None
            }

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return data

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_config(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name="setupverificacion")
    @commands.has_permissions(administrator=True)
    async def setup_verificacion(self, ctx, role: discord.Role):

        embed = discord.Embed(
            title="╭・𝐕𝐞𝐫𝐢𝐟𝐢𝐜𝐚𝐜𝐢ó𝐧・✅",
            description=(
                "Para acceder al servidor necesitás verificarte.\n\n"
                "Reaccioná con **✅** a este mensaje para verificarte.\n\n"
                "Una vez verificado, vas a recibir automáticamente el rol correspondiente."
            ),
            color=discord.Color.from_rgb(145, 70, 255)
        )

        embed.set_footer(
            text="Sistema de verificación"
        )

        message = await ctx.send(embed=embed)

        await message.add_reaction("✅")

        self.config["message_id"] = message.id
        self.config["channel_id"] = message.channel.id
        self.config["role_id"] = role.id

        self.save_config()

        await ctx.send(
            f"✅ Sistema configurado correctamente.\n"
            f"Rol de verificación: {role.mention}",
            delete_after=8
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id != self.config.get("message_id"):
            return

        if str(payload.emoji) != "✅":
            return

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        member = guild.get_member(payload.user_id)

        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                return

        role = guild.get_role(self.config.get("role_id"))

        if role is None:
            return

        if role in member.roles:
            return

        try:
            await member.add_roles(
                role,
                reason="Verificación mediante reacción"
            )

        except discord.Forbidden:
            print(
                f"[VERIFICACION] No tengo permisos para darle "
                f"el rol a {member}"
            )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        if payload.message_id != self.config.get("message_id"):
            return

        if str(payload.emoji) != "✅":
            return

        guild = self.bot.get_guild(payload.guild_id)

        if guild is None:
            return

        member = guild.get_member(payload.user_id)

        if member is None:
            try:
                member = await guild.fetch_member(payload.user_id)
            except discord.NotFound:
                return

        role = guild.get_role(self.config.get("role_id"))

        if role is None:
            return

        if role not in member.roles:
            return

        try:
            await member.remove_roles(
                role,
                reason="Se quitó la reacción de verificación"
            )

        except discord.Forbidden:
            print(
                f"[VERIFICACION] No tengo permisos para quitar "
                f"el rol a {member}"
            )


async def setup(bot):
    await bot.add_cog(Verification(bot))