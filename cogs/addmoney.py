import discord
from discord.ext import commands
from discord import app_commands

import os
import json


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(
    DATA_FOLDER,
    "economia.json"
)

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)

COIN = "💵"

# Cantidad máxima que se puede agregar de una vez
MAX_AMOUNT = 1_000_000_000


# ============================================================
# ADD MONEY
# ============================================================

class AddMoney(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        os.makedirs(
            DATA_FOLDER,
            exist_ok=True
        )

        # Crear archivo si no existe
        if not os.path.exists(DATA_FILE):

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    {},
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        print(
            "[ADDMONEY] Cog cargado correctamente."
        )

    # ========================================================
    # CARGAR ECONOMÍA
    # ========================================================

    def load_data(self):

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):
                    return data

        except Exception as e:

            print(
                f"[ADDMONEY] Error cargando economía: {e}"
            )

        return {}

    # ========================================================
    # GUARDAR ECONOMÍA
    # ========================================================

    def save_data(self, data):

        try:

            temp_file = DATA_FILE + ".tmp"

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temp_file,
                DATA_FILE
            )

            return True

        except Exception as e:

            print(
                f"[ADDMONEY] Error guardando economía: {e}"
            )

            return False

    # ========================================================
    # FORMATEAR DINERO
    # ========================================================

    def format_money(self, amount):

        return f"{amount:,}".replace(
            ",",
            "."
        )

    # ========================================================
    # CREAR USUARIO SI NO EXISTE
    # ========================================================

    def get_user(self, data, user_id):

        user_id = str(user_id)

        if user_id not in data:

            data[user_id] = {
                "money": 1000,
                "bank": 0,
                "daily": 0,
                "work": 0,
                "wins": 0,
                "losses": 0,
                "inventory": []
            }

        # Compatibilidad con cuentas viejas
        data[user_id].setdefault(
            "money",
            1000
        )

        data[user_id].setdefault(
            "bank",
            0
        )

        data[user_id].setdefault(
            "daily",
            0
        )

        data[user_id].setdefault(
            "work",
            0
        )

        data[user_id].setdefault(
            "wins",
            0
        )

        data[user_id].setdefault(
            "losses",
            0
        )

        data[user_id].setdefault(
            "inventory",
            []
        )

        return data[user_id]

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
        # VALIDACIONES
        # ====================================================

        if usuario.bot:

            await ctx.send(
                "❌ No podés agregar dinero a un bot."
            )

            return

        if cantidad <= 0:

            await ctx.send(
                "❌ La cantidad tiene que ser mayor a **0**."
            )

            return

        if cantidad > MAX_AMOUNT:

            await ctx.send(
                f"❌ La cantidad máxima es "
                f"**${self.format_money(MAX_AMOUNT)}**."
            )

            return

        # ====================================================
        # CARGAR DATA
        # ====================================================

        data = self.load_data()

        user_data = self.get_user(
            data,
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
        # GUARDAR
        # ====================================================

        if not self.save_data(data):

            # Si falla el guardado, revertimos
            user_data["money"] = old_money

            await ctx.send(
                "❌ No pude guardar el cambio en la economía."
            )

            return

        # ====================================================
        # CONFIRMACIÓN
        # ====================================================

        embed = discord.Embed(
            title="💵・DINERO AGREGADO",
            description=(
                f"Se agregó dinero correctamente.\n\n"

                f"👤 **Usuario:**\n"
                f"{usuario.mention}\n\n"

                f"💵 **Cantidad agregada:**\n"
                f"**+${self.format_money(cantidad)}**\n\n"

                f"💰 **Saldo anterior:**\n"
                f"${self.format_money(old_money)}\n\n"

                f"💎 **Nuevo saldo:**\n"
                f"**${self.format_money(new_money)}**"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=f"Agregado por {ctx.author}"
        )

        await ctx.send(
            embed=embed
        )

    # ========================================================
    # ERROR ADDMONEY
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
        # FALTA USUARIO/CANTIDAD
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            await ctx.send(
                "❌ Uso correcto:\n"
                f"`{self.get_prefix_text(ctx)}addmoney @usuario cantidad`\n\n"
                f"Ejemplo:\n"
                f"`{self.get_prefix_text(ctx)}addmoney @Valen 5000`"
            )

            return

        # ----------------------------------------------------
        # CANTIDAD INVÁLIDA
        # ----------------------------------------------------

        if isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                "❌ La cantidad debe ser un número entero válido.\n\n"
                "Ejemplo:\n"
                f"`{self.get_prefix_text(ctx)}addmoney @usuario 5000`"
            )

            return

        # ----------------------------------------------------
        # COOLDOWN / OTROS
        # ----------------------------------------------------

        print(
            f"[ADDMONEY] Error: {error}"
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


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        AddMoney(bot)
    )