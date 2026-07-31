import discord
from discord import app_commands
from discord.ext import commands
class AddXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ============================================================
    # /ADDXP
    # ============================================================
    @app_commands.command(
        name="addxp",
        description="Agrega una cantidad de XP a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés agregar XP.",
        cantidad="Cantidad de XP que querés agregar."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def addxp(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: app_commands.Range[int, 1, 1000000]
    ):
        # Comprobar servidor
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return
        # ========================================================
        # BUSCAR EL COG DE XP
        # ========================================================
        xp_cog = self.bot.get_cog("XP")
        if xp_cog is None:
            await interaction.response.send_message(
                "❌ El sistema de XP no está cargado.",
                ephemeral=True
            )
            return
        # ========================================================
        # OBTENER DATOS DEL USUARIO
        # ========================================================
        user_data = xp_cog.get_user_data(
            interaction.guild.id,
            usuario.id
        )
        old_level = user_data["level"]
        # ========================================================
        # AGREGAR XP
        # ========================================================
        user_data["xp"] += cantidad
        # ========================================================
        # CALCULAR NIVEL
        # ========================================================
        new_level, remaining_xp = xp_cog.calculate_level(
            user_data["xp"]
        )
        user_data["level"] = new_level
        user_data["xp"] = remaining_xp
        # ========================================================
        # GUARDAR
        # ========================================================
        # Usar la función del Cog XP
        import os
        import json
        data_folder = "data"
        data_file = os.path.join(
            data_folder,
            "xp.json"
        )
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        with open(
            data_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                xp_cog.data,
                file,
                indent=4,
                ensure_ascii=False
            )
        # ========================================================
        # RECOMPENSAS
        # ========================================================
        rewards = []
        if new_level > old_level:
            for level in range(
                old_level + 1,
                new_level + 1
            ):
                reward = await xp_cog.give_level_reward(
                    usuario,
                    level
                )
                if reward:
                    rewards.append(
                        reward.name
                    )
        # ========================================================
        # EMBED
        # ========================================================
        embed = discord.Embed(
            title="✨ XP agregada",
            description=(
                f"Se agregaron **{cantidad:,} XP** "
                f"a {usuario.mention}."
            ),
            colour=discord.Colour.green()
        )
        embed.add_field(
            name="🏆 Nivel actual",
            value=f"**{new_level}**",
            inline=True
        )
        embed.add_field(
            name="✨ XP actual",
            value=(
                f"**{user_data['xp']:,}** / "
                f"**{xp_cog.xp_required(new_level):,}**"
            ),
            inline=True
        )
        if rewards:
            embed.add_field(
                name="🎁 Recompensas obtenidas",
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
    # ============================================================
    # MANEJO DE ERRORES
    # ============================================================
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
        elif isinstance(
            error,
            app_commands.errors.TransformerError
        ):
            message = (
                "❌ La cantidad de XP debe ser "
                "un número válido."
            )
        else:
            print(
                f"❌ Error en /addxp: {error}"
            )
            message = (
                "❌ Ocurrió un error al agregar XP."
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
        AddXP(bot)
    )