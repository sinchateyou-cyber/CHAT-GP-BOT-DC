import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)

COIN = "💵"

MAX_AMOUNT = 1_000_000_000


# ============================================================
# ADD MONEY
# ============================================================

class AddMoney(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print(
            "[ADDMONEY] Cog cargado correctamente."
        )

    # ========================================================
    # OBTENER COG DE ECONOMÍA
    # ========================================================

    def get_economia(self):

        economia = self.bot.get_cog("Economia")

        return economia

    # ========================================================
    # FORMATO DINERO
    # ========================================================

    def format_money(self, amount):

        return f"{amount:,}".replace(
            ",",
            "."
        )

    # ========================================================
    # PREFIX ACTUAL
    # ========================================================

    def get_prefix_text(self, ctx):

        try:

            prefix_cog = self.bot.get_cog(
                "Prefix"
            )

            if prefix_cog:

                return prefix_cog.get_prefix(
                    ctx.guild.id
                )

        except Exception:
            pass

        return "s!"

    # ========================================================
    # ADD MONEY
    # ========================================================

    @commands.hybrid_command(
        name="addmoney",
        description="Agrega dinero a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés agregar dinero.",
        cantidad="Cantidad de dinero que querés agregar."
    )
    @commands.guild_only()
    @commands.has_guild_permissions(
        administrator=True
    )
    async def addmoney(
        self,
        ctx,
        usuario: discord.Member,
        cantidad: app_commands.Range[
            int,
            1,
            MAX_AMOUNT
        ]
    ):

        # ====================================================
        # BUSCAR ECONOMÍA
        # ====================================================

        economia = self.get_economia()

        if economia is None:

            await ctx.send(
                "❌ El sistema de economía no está cargado."
            )

            print(
                "[ADDMONEY] ERROR: No se encontró el cog Economia."
            )

            return

        # ====================================================
        # VALIDAR USUARIO
        # ====================================================

        if usuario.bot:

            await ctx.send(
                "❌ No podés agregar dinero a un bot."
            )

            return

        # ====================================================
        # VALIDAR CANTIDAD
        # ====================================================

        if cantidad <= 0:

            await ctx.send(
                "❌ La cantidad debe ser mayor a **0**."
            )

            return

        if cantidad > MAX_AMOUNT:

            await ctx.send(
                f"❌ La cantidad máxima es "
                f"**${self.format_money(MAX_AMOUNT)}**."
            )

            return

        # ====================================================
        # OBTENER USUARIO DESDE ECONOMÍA
        # ====================================================

        user_data = economia.get_user(
            usuario.id
        )

        # ====================================================
        # SALDO ANTERIOR
        # ====================================================

        old_money = user_data["money"]

        # ====================================================
        # AGREGAR DINERO
        # ====================================================

        user_data["money"] += cantidad

        new_money = user_data["money"]

        # ====================================================
        # GUARDAR USANDO ECONOMIA
        # ====================================================

        economia.save_data()

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="💵・DINERO AGREGADO",
            description=(
                f"Se agregó dinero correctamente.\n\n"

                f"👤 **Usuario**\n"
                f"{usuario.mention}\n\n"

                f"💵 **Cantidad agregada**\n"
                f"**+${self.format_money(cantidad)}**\n\n"

                f"💰 **Saldo anterior**\n"
                f"${self.format_money(old_money)}\n\n"

                f"💎 **Nuevo saldo**\n"
                f"**${self.format_money(new_money)}**"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=f"Agregado por {ctx.author.display_name}"
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # ERROR
    # ========================================================

    @addmoney.error
    async def addmoney_error(
        self,
        ctx,
        error
    ):

        # ----------------------------------------------------
        # SIN PERMISOS
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás tener **Administrador** "
                "para usar este comando."
            )

            return

        # ----------------------------------------------------
        # FALTA ARGUMENTO
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            prefix = self.get_prefix_text(ctx)

            await ctx.send(
                "❌ Uso correcto:\n\n"
                f"`{prefix}addmoney @usuario cantidad`\n\n"
                f"Ejemplo:\n"
                f"`{prefix}addmoney @Valen 5000`"
            )

            return

        # ----------------------------------------------------
        # ARGUMENTO INVÁLIDO
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.BadArgument
        ):

            prefix = self.get_prefix_text(ctx)

            await ctx.send(
                "❌ La cantidad debe ser un número válido.\n\n"
                f"Ejemplo:\n"
                f"`{prefix}addmoney @usuario 5000`"
            )

            return

        # ----------------------------------------------------
        # OTRO ERROR
        # ----------------------------------------------------

        print(
            f"[ADDMONEY] Error: {error}"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        AddMoney(bot)
    )