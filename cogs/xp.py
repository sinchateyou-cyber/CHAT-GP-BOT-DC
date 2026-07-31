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
# XP que puede ganar un usuario por mensaje
XP_MIN = 15
XP_MAX = 30
# Tiempo de espera entre ganancias de XP
# 60 = 1 minuto
XP_COOLDOWN = 60
# ============================================================
# RECOMPENSAS POR NIVEL
# ============================================================
# Formato:
# nivel: "Nombre del rol"
#
# El bot creará automáticamente el rol si no existe.
LEVEL_REWARDS = {
    5: "Nivel 5",
    10: "Nivel 10",
    15: "Nivel 15",
    20: "Nivel 20",
    25: "Nivel 25",
    30: "Nivel 30",
}
# ============================================================
# FUNCIONES PARA GUARDAR Y CARGAR DATOS
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
def load_data():
    ensure_data_file()
    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except (
        json.JSONDecodeError,
        FileNotFoundError
    ):
        return {}
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
# COG XP
# ============================================================
class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        # Cooldowns:
        # {(guild_id, user_id): timestamp}
        self.cooldowns = {}
    # ========================================================
    # DATOS DEL USUARIO
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
    # XP NECESARIA PARA SUBIR DE NIVEL
    # ========================================================
    def xp_required(
        self,
        level
    ):
        # Cada nivel requiere más XP
        return 100 + (
            level * 50
        )
    # ========================================================
    # CALCULAR NIVEL SEGÚN XP
    # ========================================================
    def calculate_level(
        self,
        xp
    ):
        level = 0
        while xp >= self.xp_required(level):
            xp -= self.xp_required(level)
            level += 1
        return level, xp
    # ========================================================
    # OBTENER ROL DE RECOMPENSA
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
    # ========================================================
    # DAR RECOMPENSA DE NIVEL
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
            await member.add_roles(
                role,
                reason=(
                    f"Recompensa por alcanzar "
                    f"el nivel {level}"
                )
            )
            return role
        except discord.Forbidden:
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
        # ====================================================
        # COOLDOWN
        # ====================================================
        key = (
            guild_id,
            user_id
        )
        current_time = time.time()
        if key in self.cooldowns:
            last_xp = self.cooldowns[key]
            if (
                current_time - last_xp
                < XP_COOLDOWN
            ):
                return
        self.cooldowns[key] = current_time
        # ====================================================
        # DATOS DEL USUARIO
        # ====================================================
        user_data = self.get_user_data(
            guild_id,
            user_id
        )
        old_level = user_data["level"]
        # ====================================================
        # DAR XP
        # ====================================================
        gained_xp = random.randint(
            XP_MIN,
            XP_MAX
        )
        user_data["xp"] += gained_xp
        # ====================================================
        # CALCULAR NUEVO NIVEL
        # ====================================================
        new_level, remaining_xp = (
            self.calculate_level(
                user_data["xp"]
            )
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
        # SUBIDA DE NIVEL
        # ====================================================
        if new_level > old_level:
            reward_role = None
            # Dar recompensas de todos los niveles
            # alcanzados
            for level in range(
                old_level + 1,
                new_level + 1
            ):
                reward = await self.give_level_reward(
                    message.author,
                    level
                )
                if reward:
                    reward_role = reward
            # =================================================
            # EMBED DE NIVEL
            # =================================================
            embed = discord.Embed(
                title="🎉 ¡SUBISTE DE NIVEL!",
                description=(
                    f"¡Felicitaciones "
                    f"{message.author.mention}!\n\n"
                    f"🏆 Nuevo nivel: "
                    f"**{new_level}**\n"
                    f"✨ XP actual: "
                    f"**{remaining_xp}/"
                    f"{self.xp_required(new_level)}**"
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
            if reward_role:
                embed.add_field(
                    name="🎁 Recompensa",
                    value=(
                        f"Recibiste el rol "
                        f"{reward_role.mention}"
                    ),
                    inline=False
                )
            embed.set_footer(
                text=(
                    f"Servidor: "
                    f"{message.guild.name}"
                )
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
        level = user_data["level"]
        xp = user_data["xp"]
        needed = self.xp_required(
            level
        )
        # ====================================================
        # BARRA DE PROGRESO
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
            url=(
                user
                .display_avatar
                .url
            )
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
                "📊 Todavía no hay datos "
                "de XP.",
                ephemeral=True
            )
            return
        ranking = []
        # ====================================================
        # CREAR RANKING
        # ====================================================
        for user_id, data in (
            self.data[guild_id].items()
        ):
            ranking.append(
                (
                    int(
                        data.get(
                            "level",
                            0
                        )
                    ),
                    int(
                        data.get(
                            "xp",
                            0
                        )
                    ),
                    int(
                        user_id
                    )
                )
            )
        ranking.sort(
            key=lambda item: (
                item[0],
                item[1]
            ),
            reverse=True
        )
        ranking = ranking[:10]
        # ====================================================
        # DESCRIPCIÓN
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
            member = (
                interaction.guild
                .get_member(
                    user_id
                )
            )
            if member:
                name = (
                    member
                    .display_name
                )
            else:
                name = (
                    f"Usuario "
                    f"{user_id}"
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
        # EMBED RANKING
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
    # /XPREWARDS
    # ========================================================
    @app_commands.command(
        name="xprewards",
        description=(
            "Muestra las recompensas "
            "por nivel."
        )
    )
    async def xprewards(
        self,
        interaction: discord.Interaction
    ):
        description = ""
        for level, role in (
            LEVEL_REWARDS.items()
        ):
            description += (
                f"🏆 Nivel **{level}** "
                f"→ 🎁 **{role}**\n"
            )
        embed = discord.Embed(
            title="🎁 RECOMPENSAS DE NIVEL",
            description=description,
            colour=discord.Colour.purple()
        )
        await interaction.response.send_message(
            embed=embed
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        XP(bot)
    )