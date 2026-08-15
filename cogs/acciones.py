import discord
from discord.ext import commands
from discord import app_commands

import os
import random


# ============================================================
# CONFIGURACIÓN
# ============================================================

GIF_FOLDER = "data/gifs"

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)


# ============================================================
# GIFS / FRASES
# ============================================================

ACCIONES = {

    "hug": {
        "emoji": "🤗",
        "frases": [
            "{author} abrazó a {target} 🤗💜",
            "{author} le dio un abrazo a {target} 🫂",
            "{author} abrazó fuerte a {target} 💜",
        ]
    },

    "kiss": {
        "emoji": "💋",
        "frases": [
            "{author} le dio un beso a {target} 💋",
            "{author} besó a {target} 😳💜",
            "{author} le dio un besito a {target} 💋",
        ]
    },

    "slap": {
        "emoji": "👋",
        "frases": [
            "{author} le dio una cachetada a {target} 👋",
            "{author} le pegó un cachetazo a {target} 😭",
            "{author} abofeteó a {target} 💀",
        ]
    },

    "pat": {
        "emoji": "🫳",
        "frases": [
            "{author} le acarició la cabeza a {target} 🥺",
            "{author} le hizo pat pat a {target} 🫳💜",
            "{author} mimó a {target} 🥹",
        ]
    },

    "cuddle": {
        "emoji": "🫂",
        "frases": [
            "{author} se acurrucó con {target} 🫂💜",
            "{author} está abrazadito con {target} 🥺",
            "{author} se quedó mimando a {target} 🫂",
        ]
    },

    "love": {
        "emoji": "❤️",
        "frases": [
            "{author} le mandó mucho amor a {target} ❤️",
            "{author} quiere mucho a {target} 💜",
            "{author} llenó de amor a {target} 🥰",
        ]
    },

    "punch": {
        "emoji": "👊",
        "frases": [
            "{author} le pegó un golpe a {target} 👊",
            "{author} le dio un piñazo a {target} 💀",
            "{author} atacó a {target} 👊😭",
        ]
    },

    "bite": {
        "emoji": "🦷",
        "frases": [
            "{author} mordió a {target} 🦷",
            "{author} le pegó un mordisco a {target} 😭",
            "{author} quiso comerse a {target} 🦷💜",
        ]
    },

    "highfive": {
        "emoji": "✋",
        "frases": [
            "{author} chocó los cinco con {target} ✋",
            "{author} le dio un high five a {target} 🙌",
            "{author} y {target} hicieron high five ✋💜",
        ]
    },

    "wave": {
        "emoji": "👋",
        "frases": [
            "{author} saludó a {target} 👋",
            "{author} le hizo chau a {target} 👋💜",
            "{author} saludó feliz a {target} 🥰",
        ]
    },

    "dance": {
        "emoji": "💃",
        "frases": [
            "{author} se puso a bailar 💃",
            "{author} está bailando 🕺🔥",
            "{author} arrancó a bailar 💃💜",
        ]
    },

    "cry": {
        "emoji": "😭",
        "frases": [
            "{author} está llorando 😭",
            "{author} se puso a llorar 😭💔",
            "{author} no puede parar de llorar 🥺",
        ]
    },

    "happy": {
        "emoji": "🥳",
        "frases": [
            "{author} está re feliz 🥳",
            "{author} está festejando 🎉",
            "{author} está felizísimo/a 🥰",
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
            GIF_FOLDER,
            exist_ok=True
        )

        print(
            "[ACCIONES] Cog cargado correctamente."
        )

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

        archivos = []

        for file in os.listdir(folder):

            if file.lower().endswith(
                (
                    ".gif",
                    ".webp",
                    ".png",
                    ".jpg",
                    ".jpeg"
                )
            ):

                archivos.append(
                    os.path.join(
                        folder,
                        file
                    )
                )

        if not archivos:

            return None

        return random.choice(
            archivos
        )

    # ========================================================
    # CREAR RESPUESTA
    # ========================================================

    async def ejecutar_accion(
        self,
        ctx,
        accion,
        usuario=None
    ):

        config = ACCIONES[
            accion
        ]

        author = ctx.author.display_name

        # ----------------------------------------------------
        # SI HAY USUARIO
        # ----------------------------------------------------

        if usuario:

            if usuario.bot:

                await ctx.send(
                    "❌ No podés usar este comando con un bot."
                )

                return

            if usuario.id == ctx.author.id:

                await ctx.send(
                    "❌ No podés usar este comando con vos mismo."
                )

                return

            target = usuario.display_name

            frase = random.choice(
                config["frases"]
            ).format(
                author=author,
                target=target
            )

        # ----------------------------------------------------
        # SIN USUARIO
        # ----------------------------------------------------

        else:

            frases = [
                frase
                for frase in config["frases"]
                if "{target}" not in frase
            ]

            if frases:

                frase = random.choice(
                    frases
                ).replace(
                    "{author}",
                    author
                )

            else:

                frase = (
                    f"{author} "
                    f"está usando **{accion}** "
                    f"{config['emoji']}"
                )

        # ----------------------------------------------------
        # GIF
        # ----------------------------------------------------

        gif = self.get_random_gif(
            accion
        )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            description=(
                f"**{frase}**"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text=f"{accion.upper()} • Band Arg"
        )

        # ----------------------------------------------------
        # ENVIAR GIF
        # ----------------------------------------------------

        if gif:

            try:

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

                return

            except Exception as e:

                print(
                    f"[ACCIONES] Error enviando GIF: {e}"
                )

        # ----------------------------------------------------
        # SI NO HAY GIF
        # ----------------------------------------------------

        embed.description += (
            f"\n\n⚠️ No hay GIFs configurados "
            f"para **{accion}**."
        )

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
        description="Acariciá la cabeza de alguien."
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
    # DANCE
    # ========================================================

    @commands.hybrid_command(
        name="dance",
        description="Ponete a bailar."
    )
    async def dance(
        self,
        ctx
    ):

        await self.ejecutar_accion(
            ctx,
            "dance"
        )

    # ========================================================
    # CRY
    # ========================================================

    @commands.hybrid_command(
        name="cry",
        description="Ponete a llorar."
    )
    async def cry(
        self,
        ctx
    ):

        await self.ejecutar_accion(
            ctx,
            "cry"
        )

    # ========================================================
    # HAPPY
    # ========================================================

    @commands.hybrid_command(
        name="happy",
        description="Mostrá que estás feliz."
    )
    async def happy(
        self,
        ctx
    ):

        await self.ejecutar_accion(
            ctx,
            "happy"
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