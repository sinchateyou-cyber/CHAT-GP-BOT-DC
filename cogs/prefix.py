import os
import json
import discord
from discord.ext import commands


DATA_FOLDER = "data"
PREFIX_FILE = os.path.join(DATA_FOLDER, "prefixes.json")

DEFAULT_PREFIX = "s!"

# Límite razonable para evitar prefixes gigantes
MAX_PREFIX_LENGTH = 10


class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(PREFIX_FILE):
            self._save_prefixes({})

    # ============================================================
    # ARCHIVO
    # ============================================================

    def _load_prefixes(self):
        try:
            with open(PREFIX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, dict):
                    return data

        except (FileNotFoundError, json.JSONDecodeError):
            pass

        return {}

    def _save_prefixes(self, data):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        temp_file = PREFIX_FILE + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        os.replace(temp_file, PREFIX_FILE)

    # ============================================================
    # OBTENER PREFIX
    # ============================================================

    def get_prefix(self, guild_id):
        prefixes = self._load_prefixes()

        return prefixes.get(str(guild_id), DEFAULT_PREFIX)

    # ============================================================
    # CAMBIAR PREFIX
    # ============================================================

    @commands.hybrid_command(
        name="setprefix",
        description="Cambia el prefix del bot en este servidor."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def setprefix(self, ctx, nuevo_prefix: str):
        nuevo_prefix = nuevo_prefix.strip()

        # --------------------------------------------
        # VALIDACIÓN
        # --------------------------------------------

        if not nuevo_prefix:
            await ctx.send(
                "❌ Tenés que indicar un prefix.\n"
                f"Ejemplo: `{self.get_prefix(ctx.guild.id)}setprefix !`"
            )
            return

        if len(nuevo_prefix) > MAX_PREFIX_LENGTH:
            await ctx.send(
                f"❌ El prefix no puede tener más de "
                f"**{MAX_PREFIX_LENGTH} caracteres**."
            )
            return

        # Evitar espacios
        if any(char.isspace() for char in nuevo_prefix):
            await ctx.send(
                "❌ El prefix no puede contener espacios."
            )
            return

        # Evitar backticks
        if "`" in nuevo_prefix:
            await ctx.send(
                "❌ El prefix no puede contener `."
            )
            return

        # --------------------------------------------
        # GUARDAR
        # --------------------------------------------

        prefixes = self._load_prefixes()

        prefixes[str(ctx.guild.id)] = nuevo_prefix

        self._save_prefixes(prefixes)

        embed = discord.Embed(
            title="💜 Prefix actualizado",
            description=(
                f"El prefix de este servidor ahora es:\n\n"
                f"## `{nuevo_prefix}`\n\n"
                f"Ejemplo:\n"
                f"`{nuevo_prefix}ping`"
            ),
            color=discord.Color.from_rgb(138, 43, 226)
        )

        embed.set_footer(
            text=f"Configurado por {ctx.author}"
        )

        await ctx.send(embed=embed)

    # ============================================================
    # VER PREFIX
    # ============================================================

    @commands.hybrid_command(
        name="prefix",
        description="Muestra el prefix actual del servidor."
    )
    @commands.guild_only()
    async def prefix(self, ctx):

        actual = self.get_prefix(ctx.guild.id)

        embed = discord.Embed(
            title="💜 Prefix actual",
            description=(
                f"El prefix de **{ctx.guild.name}** es:\n\n"
                f"## `{actual}`\n\n"
                f"Ejemplo:\n"
                f"`{actual}ping`"
            ),
            color=discord.Color.from_rgb(138, 43, 226)
        )

        await ctx.send(embed=embed)

    # ============================================================
    # RESTAURAR PREFIX
    # ============================================================

    @commands.hybrid_command(
        name="resetprefix",
        description="Restablece el prefix predeterminado."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def resetprefix(self, ctx):

        prefixes = self._load_prefixes()

        guild_id = str(ctx.guild.id)

        if guild_id in prefixes:
            del prefixes[guild_id]
            self._save_prefixes(prefixes)

        embed = discord.Embed(
            title="💜 Prefix restablecido",
            description=(
                f"El prefix volvió al predeterminado:\n\n"
                f"## `{DEFAULT_PREFIX}`\n\n"
                f"Ejemplo:\n"
                f"`{DEFAULT_PREFIX}ping`"
            ),
            color=discord.Color.from_rgb(138, 43, 226)
        )

        await ctx.send(embed=embed)

    # ============================================================
    # ERRORES
    # ============================================================

    @setprefix.error
    async def setprefix_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ Necesitás el permiso **Administrador** para cambiar "
                "el prefix."
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            actual = self.get_prefix(ctx.guild.id)

            await ctx.send(
                f"❌ Indicá el nuevo prefix.\n"
                f"Ejemplo: `{actual}setprefix !`"
            )

        else:
            raise error

    @resetprefix.error
    async def resetprefix_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ Necesitás el permiso **Administrador**."
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(Prefix(bot))