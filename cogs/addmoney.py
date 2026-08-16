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

MAX_AMOUNT = 1_000_000_000


# ============================================================
# COG
# ============================================================

class AddMoney(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        os.makedirs(
            DATA_FOLDER,
            exist_ok=True
        )

        print(
            "[ADDMONEY] Cog cargado correctamente."
        )


    # ========================================================
    # CARGAR ECONOMÍA
    # ========================================================

    def load_data(self):

        if not os.path.exists(DATA_FILE):

            return {}

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):

                    return data

        except Exception as error:

            print(
                f"[ADDMONEY] Error cargando economía: {error}"
            )

        return {}


    # ========================================================
    # GUARDAR ECONOMÍA
    # ========================================================

    def save_data(self, data):

        try:

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

            return True

        except Exception as error:

            print(
                f"[ADDMONEY] Error guardando economía: {error}"
            )

            return False


    # ========================================================
    # FORMATO DINERO
    # ========================================================

    def format_money(
        self,
        amount
    ):

        return f"{amount:,}".replace(
            ",",
            "."
        )


    # ========================================================
    # ADD MONEY
    # ========================================================

    @commands.hybrid_command(
        name="addmoney",
        aliases=[
            "addcash",
            "givecash"
        ],
        description="Agrega dinero a un usuario."
    )
    @commands.guild_only()
    @commands.has_permissions(
        administrator=True
    )
    @app_commands.describe(
        usuario="Usuario al que se le agregará dinero.",
        cantidad="Cantidad de dinero a agregar."
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

        # ----------------------------------------------------
        # BOTS
        # ----------------------------------------------------

        if usuario.bot:

            await ctx.send(
                "❌ No podés agregar dinero a un bot."
            )

            return


        # ----------------------------------------------------
        # CANTIDAD
        # ----------------------------------------------------

        if cantidad <= 0:

            await ctx.send(
                "❌ La cantidad debe ser mayor que **0**."
            )

            return


        if cantidad > MAX_AMOUNT:

            await ctx.send(
                f"❌ La cantidad máxima es "
                f"**${self.format_money(MAX_AMOUNT)}**."
            )

            return


        # ----------------------------------------------------
        # CARGAR DATA
        # ----------------------------------------------------

        data = self.load_data()

        user_id = str(
            usuario.id
        )


        # ----------------------------------------------------
        # CREAR USUARIO SI NO EXISTE
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # ASEGURAR MONEY
        # ----------------------------------------------------

        if "money" not in data[user_id]:

            data[user_id]["money"] = 0


        dinero_anterior = int(
            data[user_id]["money"]
        )

        nuevo_saldo = (
            dinero_anterior
            + cantidad
        )


        # ----------------------------------------------------
        # CONFIRMACIÓN
        # ----------------------------------------------------

        embed = discord.Embed(
            title="💜・CONFIRMAR DEPÓSITO",
            description=(
                f"Estás por agregar dinero a "
                f"{usuario.mention}.\n\n"

                f"👤 **Usuario**\n"
                f"{usuario.display_name}\n\n"

                f"💵 **Cantidad**\n"
                f"**${self.format_money(cantidad)}**\n\n"

                f"💰 **Saldo actual**\n"
                f"**${self.format_money(dinero_anterior)}**\n\n"

                f"📈 **Nuevo saldo**\n"
                f"**${self.format_money(nuevo_saldo)}**\n\n"

                f"¿Querés confirmar esta operación?"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}"
        )


        view = ConfirmAddMoneyView(
            author_id=ctx.author.id
        )

        await ctx.send(
            embed=embed,
            view=view
        )

        await view.wait()


        # ----------------------------------------------------
        # CANCELADO
        # ----------------------------------------------------

        if not view.confirmed:

            return


        # ----------------------------------------------------
        # VOLVER A CARGAR DATA
        #
        # Esto evita sobrescribir cambios hechos
        # mientras el administrador confirmaba.
        # ----------------------------------------------------

        data = self.load_data()

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


        if "money" not in data[user_id]:

            data[user_id]["money"] = 0


        saldo_anterior = int(
            data[user_id]["money"]
        )

        saldo_nuevo = (
            saldo_anterior
            + cantidad
        )

        data[user_id]["money"] = saldo_nuevo


        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        if not self.save_data(data):

            await ctx.send(
                "❌ No se pudo guardar la operación."
            )

            return


        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        embed = discord.Embed(
            title="💰・DINERO AGREGADO",
            description=(
                f"Se agregaron correctamente "
                f"**${self.format_money(cantidad)}** "
                f"a {usuario.mention}.\n\n"

                f"💵 **Cantidad agregada**\n"
                f"**${self.format_money(cantidad)}**\n\n"

                f"💰 **Saldo anterior**\n"
                f"**${self.format_money(saldo_anterior)}**\n\n"

                f"📈 **Nuevo saldo**\n"
                f"**${self.format_money(saldo_nuevo)}**"
            ),
            color=PURPLE
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=f"Operación realizada por {ctx.author.display_name}"
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# VIEW DE CONFIRMACIÓN
# ============================================================

class ConfirmAddMoneyView(
    discord.ui.View
):

    def __init__(
        self,
        author_id
    ):

        super().__init__(
            timeout=30
        )

        self.author_id = author_id
        self.confirmed = False


    # ========================================================
    # CONFIRMAR
    # ========================================================

    @discord.ui.button(
        label="Confirmar",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Solo el administrador que inició "
                "la operación puede confirmarla.",
                ephemeral=True
            )

            return


        self.confirmed = True

        for child in self.children:

            child.disabled = True

        await interaction.response.edit_message(
            content="✅ Operación confirmada.",
            embed=None,
            view=self
        )

        self.stop()


    # ========================================================
    # CANCELAR
    # ========================================================

    @discord.ui.button(
        label="Cancelar",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(
                "❌ Solo el administrador que inició "
                "la operación puede cancelarla.",
                ephemeral=True
            )

            return


        self.confirmed = False

        for child in self.children:

            child.disabled = True

        await interaction.response.edit_message(
            content="❌ Operación cancelada.",
            embed=None,
            view=self
        )

        self.stop()


    # ========================================================
    # TIMEOUT
    # ========================================================

    async def on_timeout(self):

        for child in self.children:

            child.disabled = True


# ============================================================
# ERROR HANDLER
# ============================================================

    @addmoney.error
    async def addmoney_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ Necesitás permisos de **Administrador** "
                "para utilizar este comando."
            )

            return


        if isinstance(
            error,
            commands.MemberNotFound
        ):

            await ctx.send(
                "❌ No encontré a ese usuario."
            )

            return


        if isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            await ctx.send(
                "❌ Uso correcto:\n"
                "`s!addmoney @usuario 5000`"
            )

            return


        if isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                "❌ Revisá los datos ingresados.\n\n"
                "Ejemplo:\n"
                "`s!addmoney @usuario 5000`"
            )

            return


        print(
            f"[ADDMONEY] Error: "
            f"{type(error).__name__}: {error}"
        )

        await ctx.send(
            "❌ Ocurrió un error al agregar el dinero."
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        AddMoney(bot)
    )