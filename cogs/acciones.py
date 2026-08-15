import discord
from discord.ext import commands
from discord import app_commands

import os
import json
import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

GIF_FOLDER = "data/gifs"
DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "acciones.json")

PURPLE = discord.Color.from_rgb(115, 55, 210)


# ============================================================
# ACCIONES
# ============================================================

ACCIONES = {
    "hug": {
        "emoji": "🤗",
        "nombre": "abrazos",
        "frases": [
            "{author} abrazó a {target} 🤗💜",
            "{author} le dio un abrazo a {target} 🫂",
            "{author} abrazó fuerte a {target} 💜",
        ]
    },

    "kiss": {
        "emoji": "💋",
        "nombre": "besos",
        "frases": [
            "{author} le dio un beso a {target} 💋",
            "{author} besó a {target} 😳💜",
            "{author} le dio un besito a {target} 💋",
        ]
    },

    "slap": {
        "emoji": "👋",
        "nombre": "cachetadas",
        "frases": [
            "{author} le dio una cachetada a {target} 👋",
            "{author} le pegó un cachetazo a {target} 😭",
            "{author} abofeteó a {target} 💀",
        ]
    },

    "pat": {
        "emoji": "🫳",
        "nombre": "pat",
        "frases": [
            "{author} le acarició la cabeza a {target} 🥺",
            "{author} le hizo pat pat a {target} 🫳💜",
            "{author} mimó a {target} 🥹",
        ]
    },

    "cuddle": {
        "emoji": "🫂",
        "nombre": "cuddles",
        "frases": [
            "{author} se acurrucó con {target} 🫂💜",
            "{author} está abrazadito con {target} 🥺",
            "{author} se quedó mimando a {target} 🫂",
        ]
    },

    "love": {
        "emoji": "❤️",
        "nombre": "amores",
        "frases": [
            "{author} le mandó mucho amor a {target} ❤️",
            "{author} quiere mucho a {target} 💜",
            "{author} llenó de amor a {target} 🥰",
        ]
    },

    "punch": {
        "emoji": "👊",
        "nombre": "golpes",
        "frases": [
            "{author} le pegó un golpe a {target} 👊",
            "{author} le dio un piñazo a {target} 💀",
            "{author} atacó a {target} 👊😭",
        ]
    },

    "bite": {
        "emoji": "🦷",
        "nombre": "mordidas",
        "frases": [
            "{author} mordió a {target} 🦷",
            "{author} le pegó un mordisco a {target} 😭",
            "{author} quiso comerse a {target} 🦷💜",
        ]
    },

    "highfive": {
        "emoji": "✋",
        "nombre": "high fives",
        "frases": [
            "{author} chocó los cinco con {target} ✋",
            "{author} le dio un high five a {target} 🙌",
            "{author} y {target} hicieron high five ✋💜",
        ]
    },

    "wave": {
        "emoji": "👋",
        "nombre": "saludos",
        "frases": [
            "{author} saludó a {target} 👋",
            "{author} le hizo chau a {target} 👋💜",
            "{author} saludó feliz a {target} 🥰",
        ]
    }
}


# ============================================================
# COG
# ============================================================

class Acciones(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        os.makedirs(
            DATA_FOLDER,
            exist_ok=True
        )

        os.makedirs(
            GIF_FOLDER,
            exist_ok=True
        )

        self.data = self.load_data()

        print(
            "[ACCIONES] Cog cargado correctamente."
        )

    # ========================================================
    # CARGAR DATA
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

        except Exception as e:

            print(
                f"[ACCIONES] Error cargando JSON: {e}"
            )

        return {}

    # ========================================================
    # GUARDAR DATA
    # ========================================================

    def save_data(self):

        try:

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            print(
                f"[ACCIONES] Error guardando JSON: {e}"
            )

    # ========================================================
    # CREAR USUARIO
    # ========================================================

    def ensure_user(
        self,
        user_id
    ):

        user_id = str(user_id)

        if user_id not in self.data:

            self.data[user_id] = {
                "received": {},
                "given": {},
                "last_received": {}
            }

        self.data[user_id].setdefault(
            "received",
            {}
        )

        self.data[user_id].setdefault(
            "given",
            {}
        )

        self.data[user_id].setdefault(
            "last_received",
            {}
        )

        return self.data[user_id]

    # ========================================================
    # OBTENER GIF
    # ========================================================

    def get_random_gif(
        self,
        accion
    ):

        folder = os.path.join(
            GIF_FOLDER,
            accion
        )

        if not os.path.exists(folder):

            return None

        files = []

        for filename in os.listdir(folder):

            if filename.lower().endswith(
                (
                    ".gif",
                    ".webp",
                    ".png",
                    ".jpg",
                    ".jpeg"
                )
            ):

                files.append(
                    os.path.join(
                        folder,
                        filename
                    )
                )

        if not files:

            return None

        return random.choice(files)

    # ========================================================
    # REGISTRAR ACCIÓN
    # ========================================================

    def register_action(
        self,
        sender_id,
        receiver_id,
        accion
    ):

        sender = self.ensure_user(
            sender_id
        )

        receiver = self.ensure_user(
            receiver_id
        )

        sender["given"][accion] = (
            sender["given"].get(
                accion,
                0
            ) + 1
        )

        receiver["received"][accion] = (
            receiver["received"].get(
                accion,
                0
            ) + 1
        )

        receiver["last_received"][accion] = str(
            sender_id
        )

        self.save_data()

    # ========================================================
    # EJECUTAR ACCIÓN
    # ========================================================

    async def ejecutar_accion(
        self,
        ctx,
        accion,
        usuario=None,
        devolver=False
    ):

        config = ACCIONES[accion]

        author = ctx.author.display_name

        # ----------------------------------------------------
        # SIN USUARIO
        # ----------------------------------------------------

        if usuario is None:

            # Intentar devolver la última acción recibida
            if devolver:

                user_data = self.ensure_user(
                    ctx.author.id
                )

                last_id = user_data[
                    "last_received"
                ].get(
                    accion
                )

                if last_id:

                    try:

                        usuario = ctx.guild.get_member(
                            int(last_id)
                        )

                    except Exception:

                        usuario = None

            # Si no hay persona
            if usuario is None:

                frases = [
                    x
                    for x in config["frases"]
                    if "{target}" not in x
                ]

                if frases:

                    frase = random.choice(
                        frases
                    ).format(
                        author=author
                    )

                else:

                    frase = (
                        f"{author} "
                        f"usó **{accion}** "
                        f"{config['emoji']}"
                    )

                gif = self.get_random_gif(
                    accion
                )

                embed = discord.Embed(
                    description=f"**{frase}**",
                    color=PURPLE
                )

                if gif:

                    file = discord.File(
                        gif,
                        filename="accion.gif"
                    )

                    embed.set_image(
                        url="attachment://accion.gif"
                    )

                    await ctx.send(
                        embed=embed,
                        file=file
                    )

                else:

                    await ctx.send(
                        embed=embed
                    )

                return

        # ----------------------------------------------------
        # VALIDACIONES
        # ----------------------------------------------------

        if usuario.bot:

            await ctx.send(
                "❌ No podés usar este comando con un bot."
            )

            return

        if usuario.id == ctx.author.id:

            await ctx.send(
                "❌ No podés hacerte esta acción a vos mismo."
            )

            return

        # ----------------------------------------------------
        # DEVOLVER
        # ----------------------------------------------------

        if devolver:

            frase = (
                f"{author} devolvió el "
                f"{config['nombre'][:-1] if config['nombre'].endswith('s') else config['nombre']} "
                f"a {usuario.display_name} "
                f"{config['emoji']}"
            )

        else:

            frase = random.choice(
                config["frases"]
            ).format(
                author=author,
                target=usuario.display_name
            )

        # ----------------------------------------------------
        # GUARDAR ESTADÍSTICA
        # ----------------------------------------------------

        self.register_action(
            ctx.author.id,
            usuario.id,
            accion
        )

        # ----------------------------------------------------
        # OBTENER TOTAL RECIBIDO
        # ----------------------------------------------------

        receiver_data = self.ensure_user(
            usuario.id
        )

        total = receiver_data[
            "received"
        ].get(
            accion,
            0
        )

        # ----------------------------------------------------
        # GIF
        # ----------------------------------------------------

        gif = self.get_random_gif(
            accion
        )

        embed = discord.Embed(
            description=(
                f"**{frase}**\n\n"
                f"{config['emoji']} "
                f"{usuario.display_name} recibió "
                f"**{total} {config['nombre']}**."
            ),
            color=PURPLE
        )

        embed.set_footer(
            text=f"{accion.upper()} • Band Arg"
        )

        if gif:

            file = discord.File(
                gif,
                filename="accion.gif"
            )

            embed.set_image(
                url="attachment://accion.gif"
            )

            await ctx.send(
                embed=embed,
                file=file
            )

        else:

            await ctx.send(
                embed=embed
            )

    # ========================================================
    # HUG
    # ========================================================

    @commands.hybrid_command(
        name="hug",
        description="Abrazá a alguien."
    )
    @app_commands.describe(
        usuario="Usuario que querés abrazar."
    )
    async def hug(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "hug",
            usuario
        )

    # ========================================================
    # KISS
    # ========================================================

    @commands.hybrid_command(
        name="kiss",
        description="Dale un beso a alguien."
    )
    @app_commands.describe(
        usuario="Usuario que querés besar."
    )
    async def kiss(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "kiss",
            usuario
        )

    # ========================================================
    # SLAP
    # ========================================================

    @commands.hybrid_command(
        name="slap",
        description="Dale una cachetada a alguien."
    )
    @app_commands.describe(
        usuario="Usuario que querés cachetear."
    )
    async def slap(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "slap",
            usuario
        )

    # ========================================================
    # PAT
    # ========================================================

    @commands.hybrid_command(
        name="pat",
        description="Acariciá a alguien."
    )
    @app_commands.describe(
        usuario="Usuario que querés mimar."
    )
    async def pat(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "pat",
            usuario
        )

    # ========================================================
    # CUDDLE
    # ========================================================

    @commands.hybrid_command(
        name="cuddle",
        description="Acurrucate con alguien."
    )
    @app_commands.describe(
        usuario="Usuario con quien querés acurrucarte."
    )
    async def cuddle(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "cuddle",
            usuario
        )

    # ========================================================
    # LOVE
    # ========================================================

    @commands.hybrid_command(
        name="love",
        description="Mandale amor a alguien."
    )
    @app_commands.describe(
        usuario="Usuario al que querés mandar amor."
    )
    async def love(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "love",
            usuario
        )

    # ========================================================
    # PUNCH
    # ========================================================

    @commands.hybrid_command(
        name="punch",
        description="Dale un golpe a alguien."
    )
    @app_commands.describe(
        usuario="Usuario al que querés pegarle."
    )
    async def punch(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "punch",
            usuario
        )

    # ========================================================
    # BITE
    # ========================================================

    @commands.hybrid_command(
        name="bite",
        description="Mordé a alguien."
    )
    @app_commands.describe(
        usuario="Usuario que querés morder."
    )
    async def bite(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "bite",
            usuario
        )

    # ========================================================
    # HIGH FIVE
    # ========================================================

    @commands.hybrid_command(
        name="highfive",
        description="Chocá los cinco con alguien."
    )
    @app_commands.describe(
        usuario="Usuario con quien querés hacer high five."
    )
    async def highfive(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "highfive",
            usuario
        )

    # ========================================================
    # WAVE
    # ========================================================

    @commands.hybrid_command(
        name="wave",
        description="Saludá a alguien."
    )
    @app_commands.describe(
        usuario="Usuario al que querés saludar."
    )
    async def wave(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        await self.ejecutar_accion(
            ctx,
            "wave",
            usuario
        )

    # ========================================================
    # DEVOLVER BESOS
    # ========================================================

    @commands.hybrid_command(
        name="returnkiss",
        description="Devolvé el último beso recibido."
    )
    async def returnkiss(
        self,
        ctx
    ):

        await self.ejecutar_accion(
            ctx,
            "kiss",
            None,
            True
        )

    # ========================================================
    # DEVOLVER ABRAZO
    # ========================================================

    @commands.hybrid_command(
        name="returnhug",
        description="Devolvé el último abrazo recibido."
    )
    async def returnhug(
        self,
        ctx
    ):

        await self.ejecutar_accion(
            ctx,
            "hug",
            None,
            True
        )

    # ========================================================
    # ESTADÍSTICAS
    # ========================================================

    @commands.hybrid_command(
        name="actionstats",
        description="Muestra las estadísticas de acciones."
    )
    @app_commands.describe(
        usuario="Usuario que querés consultar."
    )
    async def actionstats(
        self,
        ctx,
        usuario: discord.Member = None
    ):

        usuario = (
            usuario
            or ctx.author
        )

        data = self.ensure_user(
            usuario.id
        )

        received = data.get(
            "received",
            {}
        )

        description = ""

        for accion, config in ACCIONES.items():

            cantidad = received.get(
                accion,
                0
            )

            description += (
                f"{config['emoji']} "
                f"**{config['nombre'].capitalize()}:** "
                f"{cantidad}\n"
            )

        embed = discord.Embed(
            title=(
                f"💜・ESTADÍSTICAS DE "
                f"{usuario.display_name.upper()}"
            ),
            description=description,
            color=PURPLE
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Acciones(bot)
    )

    print(
        "[ACCIONES] Sistema de acciones activado."
    )