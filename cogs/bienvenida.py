import discord
from discord.ext import commands
import json
import os
from datetime import datetime


CONFIG_FILE = "data/bienvenida.json"


def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        os.makedirs("data", exist_ok=True)

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


class Bienvenida(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = cargar_config()


    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild_id = str(member.guild.id)

        if guild_id not in self.config:
            return


        canal_id = self.config[guild_id].get("canal")

        if not canal_id:
            return


        canal = member.guild.get_channel(
            canal_id
        )

        if not canal:
            return


        embed = discord.Embed(
            title="✨ ¡Nuevo miembro!",
            description=(
                f"Bienvenido/a {member.mention}\n\n"
                f"🎉 Ahora somos **{member.guild.member_count} miembros**\n\n"
                "Esperamos que disfrutes tu estadía 💜"
            ),
            color=discord.Color.from_rgb(
                120,
                0,
                255
            ),
            timestamp=datetime.now()
        )


        embed.set_thumbnail(
            url=member.display_avatar.url
        )


        if member.guild.icon:
            embed.set_image(
                url=member.guild.icon.url
            )


        embed.set_footer(
            text=f"{member.guild.name} • Bienvenido"
        )


        await canal.send(
            embed=embed
        )


    @commands.command(
        name="setbienvenida"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def set_bienvenida(
        self,
        ctx,
        canal: discord.TextChannel
    ):

        guild_id = str(ctx.guild.id)

        self.config[guild_id] = {
            "canal": canal.id
        }

        guardar_config(
            self.config
        )


        await ctx.send(
            f"✅ Canal de bienvenida configurado en {canal.mention}"
        )



async def setup(bot):
    await bot.add_cog(
        Bienvenida(bot)
    )