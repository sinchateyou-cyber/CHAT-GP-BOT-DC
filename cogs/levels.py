import os
import json
import random
import discord

from discord import app_commands
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = "data/levels.json"

XP_MIN = 10
XP_MAX = 25

MESSAGE_COOLDOWN = 60


# ============================================================
# FUNCIONES DE DATOS
# ============================================================

def load_data():

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                {},
                file,
                indent=4
            )

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# ============================================================
# SISTEMA DE NIVELES
# ============================================================

class Levels(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = load_data()

        # Evita que un usuario gane XP
        # por cada mensaje enviado
        self.cooldowns = {}


    # ========================================================
    # OBTENER DATOS
    # ========================================================

    def get_user_data(
        self,
        guild_id,
        user_id
    ):

        guild_id = str(guild_id)
        user_id = str(user_id)

        if guild_id not in self.data:

            self.data[guild_id] = {}

        if user_id not in self.data[guild_id]:

            self.data[guild_id][user_id] = {
                "xp": 0,
                "level": 0
            }

        return self.data[guild_id][user_id]


    # ========================================================
    # CALCULAR XP NECESARIA
    # ========================================================

    def xp_needed(
        self,
        level
    ):

        return 100 * (level + 1)


    # ========================================================
    # MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message
    ):

        # Ignorar bots
        if message.author.bot:
            return

        # Ignorar mensajes privados
        if message.guild is None:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        key = (
            guild_id,
            user_id
        )

        # ====================================================
        # COOLDOWN
        # ====================================================

        import time

        now = time.time()

        if key in self.cooldowns:

            if now - self.cooldowns[key] < MESSAGE_COOLDOWN:

                return

        self.cooldowns[key] = now


        # ====================================================
        # DAR XP
        # ====================================================

        user = self.get_user_data(
            guild_id,
            user_id
        )

        xp_gained = random.randint(
            XP_MIN,
            XP_MAX
        )

        user["xp"] += xp_gained


        # ====================================================
        # COMPROBAR NIVEL
        # ====================================================

        old_level = user["level"]

        while user["xp"] >= self.xp_needed(
            user["level"]
        ):

            user["xp"] -= self.xp_needed(
                user["level"]
            )

            user["level"] += 1


        new_level = user["level"]


        # ====================================================
        # GUARDAR
        # ====================================================

        save_data(
            self.data
        )


        # ====================================================
        # SUBIDA DE NIVEL
        # ========================================================

        if new_level > old_level:

            embed = discord.Embed(

                title="🎉 ¡Subiste de nivel!",

                description=(
                    f"¡Felicitaciones {message.author.mention}!\n\n"
                    f"Ahora sos **Nivel {new_level}**."
                ),

                colour=discord.Colour.blurple()
            )

            embed.set_thumbnail(
                url=message.author.display_avatar.url
            )

            await message.channel.send(
                embed=embed
            )


    # ========================================================
    # /LEVEL
    # ========================================================

    @app_commands.command(

        name="level",

        description=(
            "Muestra tu nivel y experiencia."
        )
    )
    @app_commands.describe(

        usuario=(
            "Usuario del que querés ver el nivel."
        )
    )
    async def level(

        self,

        interaction: discord.Interaction,

        usuario: discord.Member | None = None

    ):

        if interaction.guild is None:

            await interaction.response.send_message(

                "❌ Este comando solo funciona "
                "en servidores.",

                ephemeral=True
            )

            return


        user = usuario or interaction.user


        data = self.get_user_data(

            interaction.guild.id,

            user.id

        )


        level = data["level"]

        xp = data["xp"]

        needed = self.xp_needed(
            level
        )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(

            title="🏆 Perfil de nivel",

            description=(
                f"👤 Usuario: {user.mention}\n\n"
                f"🏆 Nivel: **{level}**\n"
                f"✨ XP: **{xp}/{needed}**"
            ),

            colour=discord.Colour.blurple()
        )


        embed.set_thumbnail(

            url=user.display_avatar.url

        )


        embed.set_footer(

            text=(
                f"Servidor: "
                f"{interaction.guild.name}"
            )

        )


        await interaction.response.send_message(

            embed=embed

        )


    # ========================================================
    # /RANK
    # ========================================================

    @app_commands.command(

        name="rank",

        description=(
            "Muestra el ranking de niveles."
        )
    )
    async def rank(

        self,

        interaction: discord.Interaction

    ):

        if interaction.guild is None:

            await interaction.response.send_message(

                "❌ Este comando solo funciona "
                "en servidores.",

                ephemeral=True

            )

            return


        guild_id = str(
            interaction.guild.id
        )


        if guild_id not in self.data:

            await interaction.response.send_message(

                "📊 Todavía no hay usuarios "
                "en el ranking.",

                ephemeral=True

            )

            return


        users = []


        for user_id, data in self.data[guild_id].items():

            users.append(

                (

                    int(data["level"]),

                    int(data["xp"]),

                    int(user_id)

                )

            )


        users.sort(

            key=lambda x: (

                x[0],

                x[1]

            ),

            reverse=True

        )


        users = users[:10]


        description = ""


        for position, (

            level,

            xp,

            user_id

        ) in enumerate(

            users,

            start=1

        ):

            member = interaction.guild.get_member(
                user_id
            )


            if member:

                name = member.display_name

            else:

                name = f"Usuario {user_id}"


            description += (

                f"**#{position}** "
                f"{name}\n"
                f"🏆 Nivel: `{level}` | "
                f"✨ XP: `{xp}`\n\n"

            )


        embed = discord.Embed(

            title="🏆 Ranking de niveles",

            description=description,

            colour=discord.Colour.gold()

        )


        await interaction.response.send_message(

            embed=embed

        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Levels(bot)
    )