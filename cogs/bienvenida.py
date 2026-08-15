import discord
from discord.ext import commands
from discord import app_commands

import json
import os
from datetime import datetime


# ============================================================
# CONFIGURACIÓN
# ============================================================

CONFIG_FILE = "data/bienvenida.json"

PURPLE = discord.Color.from_rgb(
    120,
    0,
    255
)


# ============================================================
# CARGAR CONFIG
# ============================================================

def cargar_config():

    os.makedirs(
        "data",
        exist_ok=True
    )

    if not os.path.exists(
        CONFIG_FILE
    ):

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {},
                f,
                indent=4,
                ensure_ascii=False
            )

    try:

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if isinstance(
                data,
                dict
            ):

                return data

    except Exception as e:

        print(
            f"[BIENVENIDA] Error cargando config: {e}"
        )

    return {}


# ============================================================
# GUARDAR CONFIG
# ============================================================

def guardar_config(
    data
):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# COG
# ============================================================

class Bienvenida(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.config = cargar_config()

        print(
            "[BIENVENIDA] Cog cargado correctamente."
        )

    # ========================================================
    # GUARDAR
    # ========================================================

    def save(
        self
    ):

        guardar_config(
            self.config
        )

    # ========================================================
    # VARIABLES
    # ========================================================

    def reemplazar_variables(
        self,
        texto,
        member
    ):

        texto = texto.replace(
            "{usuario}",
            member.mention
        )

        texto = texto.replace(
            "{nombre}",
            member.display_name
        )

        texto = texto.replace(
            "{servidor}",
            member.guild.name
        )

        texto = texto.replace(
            "{miembros}",
            str(
                member.guild.member_count
            )
        )

        return texto

    # ========================================================
    # MEMBER JOIN
    # ========================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        guild_id = str(
            member.guild.id
        )

        if guild_id not in self.config:

            return

        config = self.config[
            guild_id
        ]

        canal_id = config.get(
            "canal"
        )

        if not canal_id:

            return

        canal = member.guild.get_channel(
            canal_id
        )

        if not canal:

            return

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        mensaje = config.get(
            "mensaje",
            (
                "Bienvenido/a {usuario}\n\n"
                "🎉 Ahora somos **{miembros} miembros**\n\n"
                "Esperamos que disfrutes tu estadía 💜"
            )
        )

        mensaje = self.reemplazar_variables(
            mensaje,
            member
        )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title=config.get(
                "titulo",
                "✨ ¡Nuevo miembro!"
            ),
            description=mensaje,
            color=PURPLE,
            timestamp=datetime.now()
        )

        # ----------------------------------------------------
        # AVATAR
        # ----------------------------------------------------

        if config.get(
            "avatar",
            True
        ):

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

        # ----------------------------------------------------
        # BANNER / ICONO
        # ----------------------------------------------------

        if config.get(
            "icono_servidor",
            True
        ):

            if member.guild.icon:

                embed.set_image(
                    url=member.guild.icon.url
                )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        embed.set_footer(
            text=config.get(
                "footer",
                f"{member.guild.name} • Bienvenido"
            )
        )

        # ----------------------------------------------------
        # ENVIAR
        # ----------------------------------------------------

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                f"[BIENVENIDA] No tengo permisos "
                f"para enviar mensajes en #{canal.name}."
            )

        except Exception as e:

            print(
                f"[BIENVENIDA] Error enviando bienvenida: {e}"
            )

    # ========================================================
    # SET BIENVENIDA
    # ========================================================

    @commands.hybrid_command(
        name="setbienvenida",
        description="Configura el canal de bienvenida."
    )
    @app_commands.describe(
        canal="Canal donde se enviará la bienvenida."
    )
    @commands.has_permissions(
        administrator=True
    )
    async def set_bienvenida(
        self,
        ctx,
        canal: discord.TextChannel
    ):

        guild_id = str(
            ctx.guild.id
        )

        # ----------------------------------------------------
        # MANTENER CONFIG EXISTENTE
        # ----------------------------------------------------

        if guild_id not in self.config:

            self.config[guild_id] = {}

        self.config[guild_id][
            "canal"
        ] = canal.id

        self.config[guild_id].setdefault(
            "titulo",
            "✨ ¡Nuevo miembro!"
        )

        self.config[guild_id].setdefault(
            "mensaje",
            (
                "Bienvenido/a {usuario}\n\n"
                "🎉 Ahora somos **{miembros} miembros**\n\n"
                "Esperamos que disfrutes tu estadía 💜"
            )
        )

        self.config[guild_id].setdefault(
            "footer",
            f"{ctx.guild.name} • Bienvenido"
        )

        self.config[guild_id].setdefault(
            "avatar",
            True
        )

        self.config[guild_id].setdefault(
            "icono_servidor",
            True
        )

        self.save()

        await ctx.send(
            f"✅ **Bienvenida configurada**\n\n"
            f"📢 Canal: {canal.mention}\n"
            f"✨ Cuando alguien entre al servidor, "
            f"recibirá automáticamente el mensaje."
        )

    # ========================================================
    # PRUEBA
    # ========================================================

    @commands.hybrid_command(
        name="testbienvenida",
        description="Prueba el mensaje de bienvenida."
    )
    @commands.has_permissions(
        administrator=True
    )
    async def test_bienvenida(
        self,
        ctx
    ):

        guild_id = str(
            ctx.guild.id
        )

        if guild_id not in self.config:

            await ctx.send(
                "❌ Primero configurá la bienvenida con "
                "`s!setbienvenida #canal`."
            )

            return

        config = self.config[
            guild_id
        ]

        mensaje = config.get(
            "mensaje",
            (
                "Bienvenido/a {usuario}\n\n"
                "🎉 Ahora somos **{miembros} miembros**\n\n"
                "Esperamos que disfrutes tu estadía 💜"
            )
        )

        mensaje = self.reemplazar_variables(
            mensaje,
            ctx.author
        )

        embed = discord.Embed(
            title=config.get(
                "titulo",
                "✨ ¡Nuevo miembro!"
            ),
            description=mensaje,
            color=PURPLE,
            timestamp=datetime.now()
        )

        if config.get(
            "avatar",
            True
        ):

            embed.set_thumbnail(
                url=ctx.author.display_avatar.url
            )

        if config.get(
            "icono_servidor",
            True
        ):

            if ctx.guild.icon:

                embed.set_image(
                    url=ctx.guild.icon.url
                )

        embed.set_footer(
            text=config.get(
                "footer",
                f"{ctx.guild.name} • Bienvenido"
            )
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Bienvenida(bot)
    )

    print(
        "[BIENVENIDA] Sistema de bienvenida activado."
    )