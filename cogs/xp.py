import os
import json
import random
import time

import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "xp.json")

# XP aleatoria que gana un usuario por mensaje
XP_MIN = 15
XP_MAX = 30

# Tiempo entre ganancias de XP
# 60 = puede ganar XP una vez por minuto
XP_COOLDOWN = 60


# ============================================================
# RECOMPENSAS POR NIVEL
# ============================================================

  LEVEL_REWARDS = {
    5: "Novato",
    10: "Activo",
    15: "Veterano",
    20: "Experto",
    30: "Élite",
    50: "Leyenda",
}

}


# ============================================================
# CREAR CARPETA Y ARCHIVO
# ============================================================

def ensure_data_file():

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


# ============================================================
# CARGAR DATOS
# ============================================================

def load_data():

    ensure_data_file()

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


# ============================================================
# GUARDAR DATOS
# ============================================================

def save_data(data):

    ensure_data_file()

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# XP NECESARIA PARA SUBIR DE NIVEL
# ============================================================

def xp_required(level):

    return 100 + (
        level * 50
    )


# ============================================================
# CALCULAR NIVEL
# ============================================================

def calculate_level(total_xp):

    level = 0

    xp_remaining = total_xp


    while xp_remaining >= xp_required(level):

        xp_remaining -= xp_required(level)

        level += 1


    return level, xp_remaining


# ============================================================
# COG XP
# ============================================================

class XP(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = load_data()

        # Cooldown de XP
        # {(guild_id, user_id): timestamp}

        self.cooldowns = {}


    # ========================================================
    # OBTENER DATOS DEL USUARIO
    # ========================================================

    def get_user_data(
        self,
        guild_id,
        user_id
    ):

        guild_id = str(
            guild_id
        )

        user_id = str(
            user_id
        )


        if guild_id not in self.data:

            self.data[guild_id] = {}


        if user_id not in self.data[guild_id]:

            self.data[guild_id][user_id] = {

                "xp": 0,

                "level": 0

            }


        return self.data[guild_id][user_id]


    # ========================================================
    # CREAR / OBTENER ROL DE RECOMPENSA
    # ========================================================

    async def get_or_create_reward_role(
        self,
        guild,
        role_name
    ):

        role = discord.utils.get(

            guild.roles,

            name=role_name

        )


        if role:

            return role


        try:

            role = await guild.create_role(

                name=role_name,

                colour=discord.Colour.blurple(),

                reason=(
                    "Recompensa automática "
                    "del sistema de XP"
                )

            )


            return role


        except discord.Forbidden:

            return None


        except discord.HTTPException:

            return None


    # ========================================================
    # DAR RECOMPENSA
    # ========================================================

    async def give_level_reward(

        self,

        member,

        level

    ):

        if level not in LEVEL_REWARDS:

            return None


        role_name = LEVEL_REWARDS[level]


        role = await self.get_or_create_reward_role(

            member.guild,

            role_name

        )


        if role is None:

            return None


        try:

            if role not in member.roles:

                await member.add_roles(

                    role,

                    reason=(
                        f"Recompensa por alcanzar "
                        f"nivel {level}"
                    )

                )


            return role


        except discord.Forbidden:

            return None


        except discord.HTTPException:

            return None


    # ========================================================
    # EVENTO: MENSAJE
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

        current_time = time.time()


        if key in self.cooldowns:

            last_time = self.cooldowns[key]


            if (

                current_time - last_time

                < XP_COOLDOWN

            ):

                return


        self.cooldowns[key] = current_time


        # ====================================================
        # OBTENER DATOS
        # ====================================================

        user_data = self.get_user_data(

            guild_id,

            user_id

        )


        old_level = int(

            user_data.get(

                "level",

                0

            )

        )


        current_xp = int(

            user_data.get(

                "xp",

                0

            )

        )


        # ====================================================
        # DAR XP
        # ====================================================

        gained_xp = random.randint(

            XP_MIN,

            XP_MAX

        )


        current_xp += gained_xp


        # ====================================================
        # CALCULAR NIVEL
        # ====================================================

        new_level, remaining_xp = calculate_level(

            current_xp

        )


        # ====================================================
        # ACTUALIZAR DATOS
        # ====================================================

        user_data["level"] = new_level

        user_data["xp"] = remaining_xp


        # ====================================================
        # GUARDAR
        # ====================================================

        save_data(

            self.data

        )


        # ====================================================
        # SUBIDA DE NIVEL
        # ====================================================

        if new_level > old_level:

            rewards = []


            for level in range(

                old_level + 1,

                new_level + 1

            ):

                reward = await self.give_level_reward(

                    message.author,

                    level

                )


                if reward:

                    rewards.append(

                        reward.name

                    )


            # =================================================
            # EMBED
            # =================================================

            embed = discord.Embed(

                title="🎉 ¡SUBISTE DE NIVEL!",

                description=(

                    f"¡Felicitaciones "
                    f"{message.author.mention}!\n\n"

                    f"🏆 Nivel: "
                    f"**{new_level}**\n"

                    f"✨ XP: "
                    f"**{remaining_xp}/"
                    f"{xp_required(new_level)}**"

                ),

                colour=discord.Colour.gold()

            )


            embed.set_thumbnail(

                url=(

                    message.author

                    .display_avatar

                    .url

                )

            )


            if rewards:

                embed.add_field(

                    name="🎁 Recompensas",

                    value="\n".join(

                        f"• {role}"

                        for role in rewards

                    ),

                    inline=False

                )


            try:

                await message.channel.send(

                    embed=embed

                )

            except discord.Forbidden:

                pass


    # ========================================================
    # /LEVEL
    # ========================================================

    @app_commands.command(

        name="level",

        description=(
            "Muestra el nivel y XP de un usuario."
        )

    )
    @app_commands.describe(

        usuario=(
            "Usuario del que querés ver "
            "el nivel."
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


        user = (

            usuario

            or interaction.user

        )


        user_data = self.get_user_data(

            interaction.guild.id,

            user.id

        )


        level = int(

            user_data["level"]

        )


        xp = int(

            user_data["xp"]

        )


        needed = xp_required(

            level

        )


        # ====================================================
        # PROGRESO
        # ====================================================

        progress = (

            xp / needed

        )


        progress = min(

            progress,

            1

        )


        filled = int(

            progress * 10

        )


        bar = (

            "🟦" * filled

            +

            "⬜" * (

                10 - filled

            )

        )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(

            title="🏆 PERFIL DE XP",

            description=(

                f"👤 Usuario: "
                f"{user.mention}\n\n"

                f"🏆 Nivel: "
                f"**{level}**\n"

                f"✨ XP: "
                f"**{xp}/{needed}**\n\n"

                f"{bar}"

            ),

            colour=discord.Colour.blurple()

        )


        embed.set_thumbnail(

            url=user.display_avatar.url

        )


        embed.set_footer(

            text=(

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
            "Muestra el ranking de XP "
            "del servidor."
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


        ranking = []


        # ====================================================
        # CREAR RANKING
        # ====================================================

        for user_id, user_data in (

            self.data[guild_id].items()

        ):

            level = int(

                user_data.get(

                    "level",

                    0

                )

            )


            xp = int(

                user_data.get(

                    "xp",

                    0

                )

            )


            ranking.append(

                (

                    level,

                    xp,

                    int(user_id)

                )

            )


        # ====================================================
        # ORDENAR
        # ====================================================

        ranking.sort(

            key=lambda item: (

                item[0],

                item[1]

            ),

            reverse=True

        )


        ranking = ranking[:10]


        # ====================================================
        # CREAR TEXTO
        # ====================================================

        description = ""


        medals = [

            "🥇",

            "🥈",

            "🥉"

        ]


        for position, (

            level,

            xp,

            user_id

        ) in enumerate(

            ranking,

            start=1

        ):


            member = interaction.guild.get_member(

                user_id

            )


            if member:

                name = member.display_name

            else:

                name = (

                    f"Usuario {user_id}"

                )


            if position <= 3:

                icon = medals[

                    position - 1

                ]

            else:

                icon = (

                    f"**#{position}**"

                )


            description += (

                f"{icon} "
                f"**{name}**\n"

                f"🏆 Nivel: "
                f"`{level}` | "

                f"✨ XP: "
                f"`{xp}`\n\n"

            )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(

            title="🏆 RANKING DE XP",

            description=(

                description

                if description

                else (

                    "Todavía no hay "
                    "usuarios en el ranking."
                )

            ),

            colour=discord.Colour.gold()

        )


        embed.set_footer(

            text=(

                f"Top 10 • "
                f"{interaction.guild.name}"

            )

        )


        await interaction.response.send_message(

            embed=embed

        )


    # ========================================================
    # /ADDXP
    # ========================================================

    @app_commands.command(

        name="addxp",

        description=(
            "Agrega XP a un usuario."
        )

    )
    @app_commands.describe(

        usuario=(
            "Usuario al que querés "
            "agregar XP."
        ),

        cantidad=(
            "Cantidad de XP a agregar "
            "(1 - 1.000.000)."
        )

    )
    @app_commands.checks.has_permissions(

        administrator=True

    )
    async def addxp(

        self,

        interaction: discord.Interaction,

        usuario: discord.Member,

        cantidad: app_commands.Range[
            int,
            1,
            1000000
        ]

    ):

        if interaction.guild is None:

            await interaction.response.send_message(

                "❌ Este comando solo funciona "
                "en servidores.",

                ephemeral=True

            )

            return


        user_data = self.get_user_data(

            interaction.guild.id,

            usuario.id

        )


        old_level = int(

            user_data.get(

                "level",

                0

            )

        )


        current_xp = int(

            user_data.get(

                "xp",

                0

            )

        )


        # ====================================================
        # AGREGAR XP
        # ====================================================

        current_xp += cantidad


        # ====================================================
        # CALCULAR NIVEL
        # ====================================================

        new_level, remaining_xp = calculate_level(

            current_xp

        )


        user_data["level"] = new_level

        user_data["xp"] = remaining_xp


        # ====================================================
        # GUARDAR
        # ====================================================

        save_data(

            self.data

        )


        # ====================================================
        # RECOMPENSAS
        # ====================================================

        rewards = []


        if new_level > old_level:

            for level in range(

                old_level + 1,

                new_level + 1

            ):

                reward = await self.give_level_reward(

                    usuario,

                    level

                )


                if reward:

                    rewards.append(

                        reward.name

                    )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(

            title="✨ XP agregada",

            description=(

                f"Se agregaron **{cantidad:,} XP** "
                f"a {usuario.mention}."

            ),

            colour=discord.Colour.green()

        )


        embed.add_field(

            name="🏆 Nivel",

            value=(

                f"**{old_level}** → "
                f"**{new_level}**"

            ),

            inline=True

        )


        embed.add_field(

            name="✨ XP actual",

            value=(

                f"**{remaining_xp:,}** / "
                f"**{xp_required(new_level):,}**"

            ),

            inline=True

        )


        if rewards:

            embed.add_field(

                name="🎁 Recompensas",

                value="\n".join(

                    f"• {role}"

                    for role in rewards

                ),

                inline=False

            )


        embed.set_thumbnail(

            url=usuario.display_avatar.url

        )


        embed.set_footer(

            text=(

                f"XP agregada por "
                f"{interaction.user}"

            )

        )


        await interaction.response.send_message(

            embed=embed

        )


    # ========================================================
    # /ADDLEVEL
    # ========================================================

    @app_commands.command(

        name="addlevel",

        description=(
            "Agrega niveles a un usuario."
        )

    )
    @app_commands.describe(

        usuario=(
            "Usuario al que querés "
            "agregar niveles."
        ),

        niveles=(
            "Cantidad de niveles "
            "a agregar (1 - 100)."
        )

    )
    @app_commands.checks.has_permissions(

        administrator=True

    )
    async def addlevel(

        self,

        interaction: discord.Interaction,

        usuario: discord.Member,

        niveles: app_commands.Range[
            int,
            1,
            100
        ]

    ):

        if interaction.guild is None:

            await interaction.response.send_message(

                "❌ Este comando solo funciona "
                "en servidores.",

                ephemeral=True

            )

            return


        user_data = self.get_user_data(

            interaction.guild.id,

            usuario.id

        )


        old_level = int(

            user_data.get(

                "level",

                0

            )

        )


        new_level = (

            old_level

            +

            niveles

        )


        # ====================================================
        # ACTUALIZAR NIVEL
        # ====================================================

        user_data["level"] = new_level


        # ====================================================
        # GUARDAR
        # ====================================================

        save_data(

            self.data

        )


        # ====================================================
        # RECOMPENSAS
        # ====================================================

        rewards = []


        for level in range(

            old_level + 1,

            new_level + 1

        ):

            reward = await self.give_level_reward(

                usuario,

                level

            )


            if reward:

                rewards.append(

                    reward.name

                )


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(

            title="🏆 Nivel agregado",

            description=(

                f"Se agregaron **{niveles} niveles** "
                f"a {usuario.mention}."

            ),

            colour=discord.Colour.gold()

        )


        embed.add_field(

            name="📈 Nivel anterior",

            value=(

                f"**{old_level}**"

            ),

            inline=True

        )


        embed.add_field(

            name="🏆 Nivel actual",

            value=(

                f"**{new_level}**"

            ),

            inline=True

        )


        if rewards:

            embed.add_field(

                name="🎁 Recompensas",

                value="\n".join(

                    f"• {role}"

                    for role in rewards

                ),

                inline=False

            )


        embed.set_thumbnail(

            url=usuario.display_avatar.url

        )


        embed.set_footer(

            text=(

                f"Nivel agregado por "
                f"{interaction.user}"

            )

        )


        await interaction.response.send_message(

            embed=embed

        )


    # ========================================================
    # /XPREWARDS
    # ========================================================

    @app_commands.command(

        name="xprewards",

        description=(
            "Muestra las recompensas por nivel."
        )

    )
    async def xprewards(

        self,

        interaction: discord.Interaction

    ):

        description = ""


        for level, role_name in (

            LEVEL_REWARDS.items()

        ):

            description += (

                f"🏆 Nivel **{level}** "
                f"→ 🎁 **{role_name}**\n"

            )


        embed = discord.Embed(

            title="🎁 RECOMPENSAS DE NIVEL",

            description=description,

            colour=discord.Colour.purple()

        )


        await interaction.response.send_message(

            embed=embed

        )


    # ========================================================
    # MANEJO DE ERRORES DE ADDXP
    # ========================================================

    @addxp.error
    async def addxp_error(

        self,

        interaction: discord.Interaction,

        error: app_commands.AppCommandError

    ):

        if isinstance(

            error,

            app_commands.errors.MissingPermissions

        ):

            message = (

                "❌ No tenés permisos para usar "
                "este comando.\n"

                "Necesitás ser **Administrador**."

            )

        else:

            print(

                f"❌ Error en /addxp: "
                f"{type(error).__name__}: "
                f"{error}"

            )

            message = (

                "❌ Ocurrió un error al "
                "agregar XP."

            )


        if interaction.response.is_done():

            await interaction.followup.send(

                message,

                ephemeral=True

            )

        else:

            await interaction.response.send_message(

                message,

                ephemeral=True

            )


    # ========================================================
    # MANEJO DE ERRORES DE ADDLEVEL
    # ========================================================

    @addlevel.error
    async def addlevel_error(

        self,

        interaction: discord.Interaction,

        error: app_commands.AppCommandError

    ):

        if isinstance(

            error,

            app_commands.errors.MissingPermissions

        ):

            message = (

                "❌ No tenés permisos para usar "
                "este comando.\n"

                "Necesitás ser **Administrador**."

            )

        else:

            print(

                f"❌ Error en /addlevel: "
                f"{type(error).__name__}: "
                f"{error}"

            )

            message = (

                "❌ Ocurrió un error al "
                "agregar niveles."

            )


        if interaction.response.is_done():

            await interaction.followup.send(

                message,

                ephemeral=True

            )

        else:

            await interaction.response.send_message(

                message,

                ephemeral=True

            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(

        XP(bot)

    )