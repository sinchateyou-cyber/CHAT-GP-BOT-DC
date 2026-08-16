import discord
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROL_VERIFICADO = "Verificado"

CANALES_BLOQUEADOS = {
    "🎸・𝙧𝙤𝙡𝙚𝙨",
    "𝙢𝙪𝙡𝙩𝙞𝙢𝙚𝙙𝙞𝙖・𝙧𝙤𝙡",
    "🔔・𝙖𝙣𝙪𝙣𝙘𝙞𝙤𝙨",
    "🎫・𝙩𝙞𝙘𝙠𝙚𝙩",
    "🗒️・𝙧𝙚𝙜𝙡𝙖𝙨",
    "・𝙞𝙣𝙫𝙞𝙩𝙖𝙘𝙞𝙤𝙣𝙚𝙨",
}


# ============================================================
# COG
# ============================================================

class BloqueoVerificado(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print(
            "[VERIFICADO] Sistema de bloqueo cargado."
        )

    # ========================================================
    # APLICAR PERMISOS
    # ========================================================

    async def aplicar_permisos(self, guild):

        # ----------------------------------------------------
        # Buscar rol
        # ----------------------------------------------------

        rol = discord.utils.get(
            guild.roles,
            name=ROL_VERIFICADO
        )

        if rol is None:
            print(
                f"[VERIFICADO] No encontré el rol "
                f"'{ROL_VERIFICADO}' en {guild.name}."
            )
            return

        # ----------------------------------------------------
        # Recorrer canales
        # ----------------------------------------------------

        encontrados = 0

        for channel in guild.text_channels:

            if channel.name not in CANALES_BLOQUEADOS:
                continue

            try:

                await channel.set_permissions(
                    rol,
                    view_channel=True,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    add_reactions=True
                )

                encontrados += 1

                print(
                    f"[VERIFICADO] Bloqueado escribir en "
                    f"#{channel.name}"
                )

            except discord.Forbidden:

                print(
                    f"[VERIFICADO] Sin permisos para modificar "
                    f"#{channel.name}"
                )

            except Exception as e:

                print(
                    f"[VERIFICADO] Error en "
                    f"#{channel.name}: {e}"
                )

        print(
            f"[VERIFICADO] {encontrados} canales configurados."
        )

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        # Esperar a que Discord termine de cargar
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:

            await self.aplicar_permisos(guild)

        print(
            "[VERIFICADO] Permisos aplicados correctamente."
        )

    # ========================================================
    # SI SE CREA UN CANAL NUEVO
    # ========================================================

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            return

        if channel.name not in CANALES_BLOQUEADOS:
            return

        rol = discord.utils.get(
            channel.guild.roles,
            name=ROL_VERIFICADO
        )

        if rol is None:
            return

        try:

            await channel.set_permissions(
                rol,
                view_channel=True,
                send_messages=False,
                send_messages_in_threads=False,
                create_public_threads=False,
                create_private_threads=False,
                add_reactions=True
            )

            print(
                f"[VERIFICADO] Permisos aplicados a "
                f"#{channel.name}"
            )

        except Exception as e:

            print(
                f"[VERIFICADO] Error configurando "
                f"#{channel.name}: {e}"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        BloqueoVerificado(bot)
    )