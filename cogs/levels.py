import os
import json
import time
import discord

from discord.ext import commands
from discord import app_commands

# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"

LEVELS_FILE = os.path.join(DATA_FOLDER, "levels.json")
CONFIG_FILE = os.path.join(DATA_FOLDER, "config.json")

XP_PER_MESSAGE = 1
MESSAGE_COOLDOWN = 30
XP_PER_LEVEL = 100


# ============================================================
# CREAR ARCHIVOS
# ============================================================

os.makedirs(DATA_FOLDER, exist_ok=True)

if not os.path.exists(LEVELS_FILE):
    with open(LEVELS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "level_roles": {},
                "keep_old_roles": True
            },
            f,
            indent=4
        )


# ============================================================
# FUNCIONES
# ============================================================

def load_levels():

    with open(
        LEVELS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_levels(data):

    with open(
        LEVELS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def load_config():

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_config(data):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


# ============================================================
# COG
# ============================================================

class Levels(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = load_levels()

        self.config = load_config()

        self.cooldowns = {}


    # ========================================================
    # DATOS DEL USUARIO
    # ========================================================

    def get_user(self, guild_id, user_id):

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
    # XP NECESARIA
    # ========================================================

    def xp_needed(self, level):

        return XP_PER_LEVEL * (level + 1)


    # ========================================================
    # PROGRESO
    # ========================================================

    def progress_bar(self, current, maximum):

        size = 15

        filled = int((current / maximum) * size)

        empty = size - filled

        return "🟪" * filled + "⬛" * empty
        def progress_bar(self, current, maximum):

    # ========================================================
    # ASIGNAR ROLES POR NIVEL
    # ========================================================

    async def update_level_roles(self, member: discord.Member):

        level_roles = self.config.get("level_roles", {})

        if not level_roles:
            return

        keep_old = self.config.get("keep_old_roles", True)

        roles_to_add = []
        roles_to_remove = []

        highest_role = None
        highest_level = -1

        for level_str, role_id in level_roles.items():

            level = int(level_str)

            role = member.guild.get_role(int(role_id))

            if role is None:
                continue

            if level > highest_level and self.get_user(
                member.guild.id,
                member.id
            )["level"] >= level:

                highest_level = level
                highest_role = role

        if keep_old:

            for level_str, role_id in level_roles.items():

                role = member.guild.get_role(int(role_id))

                if role is None:
                    continue

                if self.get_user(
                    member.guild.id,
                    member.id
                )["level"] >= int(level_str):

                    if role not in member.roles:
                        roles_to_add.append(role)

        else:

            for role_id in level_roles.values():

                role = member.guild.get_role(int(role_id))

                if role and role in member.roles:
                    roles_to_remove.append(role)

            if highest_role:
                roles_to_add.append(highest_role)

        if roles_to_remove:
            await member.remove_roles(
                *roles_to_remove,
                reason="Actualización de rango"
            )

        if roles_to_add:
            await member.add_roles(
                *roles_to_add,
                reason="Recompensa por nivel"
            )

    # ========================================================
    # MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        key = (message.guild.id, message.author.id)

        now = time.time()

        if key in self.cooldowns:

            if now - self.cooldowns[key] < MESSAGE_COOLDOWN:
                return

        self.cooldowns[key] = now

        user = self.get_user(
            message.guild.id,
            message.author.id
        )

        old_level = user["level"]

        user["xp"] += XP_PER_MESSAGE

        while user["xp"] >= self.xp_needed(user["level"]):

            user["xp"] -= self.xp_needed(user["level"])

            user["level"] += 1

        save_levels(self.data)

        if user["level"] > old_level:

            await self.update_level_roles(message.author)

            embed = discord.Embed(
                title="🎉 ¡Subiste de nivel!",
                description=(
                    f"¡Felicitaciones {message.author.mention}!\n\n"
                    f"Ahora sos **Nivel {user['level']}**."
                ),
                color=0x8A2BE2
            )

            embed.set_thumbnail(
                url=message.author.display_avatar.url
            )

            embed.set_footer(
                text=f"Servidor: {message.guild.name}"
            )

            await message.channel.send(
                embed=embed
            )
                # ========================================================
    # /LEVEL
    # ========================================================

    @app_commands.command(
        name="level",
        description="Muestra tu nivel."
    )
    @app_commands.describe(
        usuario="Usuario que querés consultar."
    )
    async def level(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):

        usuario = usuario or interaction.user

        data = self.get_user(
            interaction.guild.id,
            usuario.id
        )

        xp = data["xp"]
        level = data["level"]
        needed = self.xp_needed(level)

        porcentaje = int((xp / needed) * 100)

        embed = discord.Embed(
            title="🏆 Nivel",
            color=0x8A2BE2
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.add_field(
            name="Usuario",
            value=usuario.mention,
            inline=False
        )

        embed.add_field(
            name="Nivel",
            value=f"**{level}**",
            inline=True
        )

        embed.add_field(
            name="XP",
            value=f"**{xp}/{needed}**",
            inline=True
        )

        embed.add_field(
            name="Progreso",
            value=f"{self.progress_bar(xp, needed)} {porcentaje}%",
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )
            # ========================================================
    # /SETLEVELROLE
    # ========================================================

    @app_commands.command(
        name="setlevelrole",
        description="Configura un rol para un nivel."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevelrole(
        self,
        interaction: discord.Interaction,
        nivel: int,
        rol: discord.Role
    ):

        self.config["level_roles"][str(nivel)] = rol.id

        save_config(self.config)

        embed = discord.Embed(
            title="✅ Rol configurado",
            description=(
                f"**Nivel:** {nivel}\n"
                f"**Rol:** {rol.mention}"
            ),
            color=0x8A2BE2
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # /REMLEVELROLE
    # ========================================================

    @app_commands.command(
        name="remlevelrole",
        description="Elimina un rol configurado."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def remlevelrole(
        self,
        interaction: discord.Interaction,
        nivel: int
    ):

        if str(nivel) not in self.config["level_roles"]:

            await interaction.response.send_message(
                "❌ Ese nivel no tiene un rol.",
                ephemeral=True
            )

            return

        del self.config["level_roles"][str(nivel)]

        save_config(self.config)

        await interaction.response.send_message(
            f"✅ Se eliminó el rol del nivel **{nivel}**.",
            ephemeral=True
        )


    # ========================================================
    # /LEVELROLES
    # ========================================================

    @app_commands.command(
        name="levelroles",
        description="Lista los roles por nivel."
    )
    async def levelroles(
        self,
        interaction: discord.Interaction
    ):

        if not self.config["level_roles"]:

            await interaction.response.send_message(
                "No hay roles configurados."
            )

            return

        texto = ""

        for nivel, role_id in sorted(
            self.config["level_roles"].items(),
            key=lambda x: int(x[0])
        ):

            role = interaction.guild.get_role(
                int(role_id)
            )

            if role:

                texto += (
                    f"**Nivel {nivel}** ➜ {role.mention}\n"
                )

        embed = discord.Embed(
            title="🏆 Roles por nivel",
            description=texto,
            color=0x8A2BE2
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ========================================================
    # /RANK
    # ========================================================

    @app_commands.command(
        name="rank",
        description="Top 10 del servidor."
    )
    async def rank(
        self,
        interaction: discord.Interaction
    ):

        guild = str(interaction.guild.id)

        if guild not in self.data:

            await interaction.response.send_message(
                "Todavía no hay datos.",
                ephemeral=True
            )
            return

        ranking = []

        for uid, info in self.data[guild].items():

            ranking.append(
                (
                    int(uid),
                    info["level"],
                    info["xp"]
                )
            )

        ranking.sort(
            key=lambda x: (
                x[1],
                x[2]
            ),
            reverse=True
        )

        embed = discord.Embed(
            title="🏆 Ranking",
            color=0x8A2BE2
        )

        descripcion = ""

        for pos, (uid, lvl, xp) in enumerate(
            ranking[:10],
            start=1
        ):

            miembro = interaction.guild.get_member(uid)

            if miembro:

                descripcion += (
                    f"**{pos}.** {miembro.mention}\n"
                    f"Nivel **{lvl}** • {xp} XP\n\n"
                )

        if descripcion == "":
            descripcion = "No hay usuarios."

        embed.description = descripcion

        await interaction.response.send_message(
            embed=embed
        )

    # ========================================================
    # /LEADERBOARD
    # ========================================================

    @app_commands.command(
        name="leaderboard",
        description="Alias de /rank."
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction
    ):

        await self.rank.callback(
            self,
            interaction
        )
            # ========================================================
    # /SETLEVELROLE
    # ========================================================

    @app_commands.command(
        name="setlevelrole",
        description="Configura un rol para un nivel."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevelrole(
        self,
        interaction: discord.Interaction,
        nivel: int,
        rol: discord.Role
    ):

        self.config["level_roles"][str(nivel)] = rol.id

        save_config(self.config)

        embed = discord.Embed(
            title="✅ Rol configurado",
            description=(
                f"**Nivel:** {nivel}\n"
                f"**Rol:** {rol.mention}"
            ),
            color=0x8A2BE2
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    # ========================================================
    # /REMLEVELROLE
    # ========================================================

    @app_commands.command(
        name="remlevelrole",
        description="Elimina un rol configurado."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def remlevelrole(
        self,
        interaction: discord.Interaction,
        nivel: int
    ):

        if str(nivel) not in self.config["level_roles"]:

            await interaction.response.send_message(
                "❌ Ese nivel no tiene un rol.",
                ephemeral=True
            )

            return

        del self.config["level_roles"][str(nivel)]

        save_config(self.config)

        await interaction.response.send_message(
            f"✅ Se eliminó el rol del nivel **{nivel}**.",
            ephemeral=True
        )
    # ========================================================
    # /ADDXP
    # ========================================================

    @app_commands.command(
        name="addxp",
        description="Agrega XP a un usuario."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int
    ):

        data = self.get_user(
            interaction.guild.id,
            usuario.id
        )

        data["xp"] += cantidad

        while data["xp"] >= self.xp_needed(data["level"]):

            data["xp"] -= self.xp_needed(data["level"])
            data["level"] += 1

            await self.update_level_roles(usuario)

        save_levels(self.data)

        await interaction.response.send_message(
            f"✅ Se agregaron **{cantidad} XP** a {usuario.mention}",
            ephemeral=True
        )


    # ========================================================
    # /SETLEVEL
    # ========================================================

    @app_commands.command(
        name="setlevel",
        description="Cambia el nivel de un usuario."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setlevel(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        nivel: int
    ):

        data = self.get_user(
            interaction.guild.id,
            usuario.id
        )

        data["level"] = nivel
        data["xp"] = 0

        save_levels(self.data)

        await self.update_level_roles(usuario)

        await interaction.response.send_message(
            f"✅ {usuario.mention} ahora es nivel **{nivel}**.",
            ephemeral=True
        )


    # ========================================================
    # /REMOVEXP
    # ========================================================

    @app_commands.command(
        name="removexp",
        description="Quita XP a un usuario."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def removexp(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int
    ):

        data = self.get_user(
            interaction.guild.id,
            usuario.id
        )

        data["xp"] = max(
            0,
            data["xp"] - cantidad
        )

        save_levels(self.data)

        await interaction.response.send_message(
            f"✅ Se quitaron **{cantidad} XP** a {usuario.mention}",
            ephemeral=True
        )
            # ========================================================
    # SINCRONIZAR ROLES AL ENTRAR
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):

        await self.update_level_roles(member)


    # ========================================================
    # ERRORES DE PERMISOS
    # ========================================================

    @commands.Cog.listener()
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.MissingPermissions
        ):

            await interaction.response.send_message(
                "❌ No tenés permisos para usar este comando.",
                ephemeral=True
            )

        else:

            raise error
            
            
            # ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Levels(bot)
    )

    
        