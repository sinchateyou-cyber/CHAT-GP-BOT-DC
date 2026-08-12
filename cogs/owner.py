import json
import os

import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# OWNER PRINCIPAL
# ============================================================

MAIN_OWNER_ID = 1460867297500594266


# ============================================================
# ARCHIVO
# ============================================================

OWNERS_FILE = "data/owners.json"


# ============================================================
# FUNCIONES
# ============================================================

def ensure_data_folder():
    os.makedirs("data", exist_ok=True)


def load_owners():

    ensure_data_folder()

    owners = []

    if os.path.exists(OWNERS_FILE):

        try:

            with open(
                OWNERS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

                if isinstance(data, list):

                    for owner_id in data:

                        try:
                            owner_id = int(owner_id)

                            if owner_id not in owners:
                                owners.append(owner_id)

                        except (TypeError, ValueError):
                            continue

        except (
            json.JSONDecodeError,
            OSError
        ):
            pass

    # ========================================================
    # ASEGURAR OWNER PRINCIPAL
    # ========================================================

    if MAIN_OWNER_ID not in owners:

        owners.insert(
            0,
            MAIN_OWNER_ID
        )

        save_owners(owners)

    return owners


def save_owners(owners):

    ensure_data_folder()

    # Eliminar duplicados
    owners_limpios = []

    for owner_id in owners:

        try:
            owner_id = int(owner_id)
        except (TypeError, ValueError):
            continue

        if owner_id not in owners_limpios:
            owners_limpios.append(owner_id)

    # El owner principal siempre queda
    if MAIN_OWNER_ID not in owners_limpios:

        owners_limpios.insert(
            0,
            MAIN_OWNER_ID
        )

    with open(
        OWNERS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            owners_limpios,
            file,
            indent=4
        )


def is_owner(user_id: int) -> bool:

    return user_id in load_owners()


# ============================================================
# COG OWNER
# ============================================================

class Owner(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        ensure_data_folder()

        # Cargar owners al iniciar
        self.owners = load_owners()

        print(
            f"[OWNER] Owners cargados: "
            f"{len(self.owners)}"
        )

    # ========================================================
    # /SETOWNER
    # ========================================================

    @app_commands.command(
        name="setowner",
        description="Agrega un usuario como owner del bot."
    )
    @app_commands.describe(
        usuario="Usuario que será agregado como owner."
    )
    async def setowner(
        self,
        interaction: discord.Interaction,
        usuario: discord.User
    ):

        # ----------------------------------------------------
        # SOLO OWNER PRINCIPAL
        # ----------------------------------------------------

        if interaction.user.id != MAIN_OWNER_ID:

            await interaction.response.send_message(
                "❌ Solo el owner principal del bot puede "
                "usar este comando.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # CARGAR
        # ----------------------------------------------------

        owners = load_owners()

        # ----------------------------------------------------
        # YA ES OWNER
        # ----------------------------------------------------

        if usuario.id in owners:

            await interaction.response.send_message(
                f"⚠️ {usuario.mention} ya es owner del bot.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # AGREGAR
        # ----------------------------------------------------

        owners.append(
            usuario.id
        )

        save_owners(
            owners
        )

        self.owners = load_owners()

        await interaction.response.send_message(
            (
                f"✅ {usuario.mention} ahora es "
                "**owner del bot**.\n\n"
                "💾 El permiso quedó guardado "
                "permanentemente."
            ),
            ephemeral=True
        )

    # ========================================================
    # /REMOVEOWNER
    # ========================================================

    @app_commands.command(
        name="removeowner",
        description="Quita a un usuario de los owners del bot."
    )
    @app_commands.describe(
        usuario="Usuario al que se le quitará el acceso."
    )
    async def removeowner(
        self,
        interaction: discord.Interaction,
        usuario: discord.User
    ):

        # ----------------------------------------------------
        # SOLO OWNER PRINCIPAL
        # ----------------------------------------------------

        if interaction.user.id != MAIN_OWNER_ID:

            await interaction.response.send_message(
                "❌ Solo el owner principal del bot puede "
                "usar este comando.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # NO SE PUEDE QUITAR AL PRINCIPAL
        # ----------------------------------------------------

        if usuario.id == MAIN_OWNER_ID:

            await interaction.response.send_message(
                "❌ No podés quitar al owner principal.",
                ephemeral=True
            )

            return

        owners = load_owners()

        # ----------------------------------------------------
        # COMPROBAR
        # ----------------------------------------------------

        if usuario.id not in owners:

            await interaction.response.send_message(
                f"⚠️ {usuario.mention} no es owner del bot.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # QUITAR
        # ----------------------------------------------------

        owners.remove(
            usuario.id
        )

        save_owners(
            owners
        )

        self.owners = load_owners()

        await interaction.response.send_message(
            (
                f"✅ {usuario.mention} ya no es "
                "**owner del bot**."
            ),
            ephemeral=True
        )

    # ========================================================
    # /OWNERS
    # ========================================================

    @app_commands.command(
        name="owners",
        description="Muestra la lista de owners del bot."
    )
    async def owners(
        self,
        interaction: discord.Interaction
    ):

        # ----------------------------------------------------
        # SOLO OWNERS
        # ----------------------------------------------------

        if not is_owner(
            interaction.user.id
        ):

            await interaction.response.send_message(
                "❌ No tenés permisos para ver los owners.",
                ephemeral=True
            )

            return

        owners = load_owners()

        if not owners:

            await interaction.response.send_message(
                "📋 No hay owners configurados.",
                ephemeral=True
            )

            return

        lista = []

        for owner_id in owners:

            usuario = self.bot.get_user(
                owner_id
            )

            if usuario:

                lista.append(
                    f"👑 {usuario.mention} "
                    f"`{owner_id}`"
                )

            else:

                lista.append(
                    f"👑 <@{owner_id}> "
                    f"`{owner_id}`"
                )

        embed = discord.Embed(
            title="👑 Owners del bot",
            description="\n".join(lista),
            color=discord.Color.gold()
        )

        embed.set_footer(
            text=f"Total: {len(owners)} owner(s)"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Owner(bot)
    )