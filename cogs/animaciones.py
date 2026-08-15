import discord
from discord.ext import commands
import aiohttp

# ============================================================
# CONFIGURACIÓN
# ============================================================

WAIFU_API = "https://api.waifu.pics"
REQUEST_TIMEOUT = 8

ANIMATION_COLOR = discord.Color.from_rgb(
    180,
    80,
    255
)

# ============================================================
# ANIMACIONES
# ============================================================

ANIMATIONS = {
    "hug": {
        "endpoint": "hug",
        "text": "{author} abrazó a {target} 🫂"
    },
    "kiss": {
        "endpoint": "kiss",
        "text": "{author} le dio un beso a {target} 💋"
    },
    "pat": {
        "endpoint": "pat",
        "text": "{author} le acarició la cabeza a {target} 🥺"
    },
    "cuddle": {
        "endpoint": "cuddle",
        "text": "{author} se acurrucó con {target} 🫂"
    },
    "poke": {
        "endpoint": "poke",
        "text": "{author} le hizo poke a {target} 👉"
    },
    "highfive": {
        "endpoint": "highfive",
        "text": "{author} chocó los cinco con {target}! ✋"
    },
    "bite": {
        "endpoint": "bite",
        "text": "{author} mordió a {target} 😳"
    },
    "slap": {
        "endpoint": "slap",
        "text": "{author} le dio una cachetada a {target} 💥"
    },
    "punch": {
        "endpoint": "punch",
        "text": "{author} le pegó un puñetazo a {target} 👊"
    },
    "kick": {
        "endpoint": "kick",
        "text": "{author} le dio una patada a {target} 🦵"
    },
    "wave": {
        "endpoint": "wave",
        "text": "{author} saludó 👋"
    },
    "dance": {
        "endpoint": "dance",
        "text": "{author} se puso a bailar 💃"
    },
    "cry": {
        "endpoint": "cry",
        "text": "{author} se puso a llorar 😭"
    },
    "happy": {
        "endpoint": "happy",
        "text": "{author} está feliz 🥰"
    },
    "angry": {
        "endpoint": "angry",
        "text": "{author} está enojado 😡"
    },
    "blush": {
        "endpoint": "blush",
        "text": "{author} se puso rojo/a 👉👈"
    }
}


# ============================================================
# COG
# ============================================================

class Animaciones(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        print("[ANIMACIONES] Cog cargado.")

    # ========================================================
    # OBTENER GIF
    # ========================================================

    async def get_gif(self, endpoint):

        url = f"{WAIFU_API}/sfw/{endpoint}"

        timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT
        )

        try:

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(url) as response:

                    if response.status != 200:

                        print(
                            f"[ANIMACIONES] API respondió "
                            f"{response.status}"
                        )

                        return None

                    data = await response.json()

                    return data.get("url")

        except Exception as e:

            print(
                f"[ANIMACIONES] Error obteniendo GIF: {e}"
            )

            return None

    # ========================================================
    # EJECUTAR ANIMACIÓN
    # ========================================================

    async def do_animation(
        self,
        ctx,
        animation_name,
        target=None
    ):

        animation = ANIMATIONS.get(
            animation_name
        )

        if animation is None:
            return

        author = ctx.author.mention

        if target is not None:
            target_text = target.mention
        else:
            target_text = ""

        text = animation["text"].format(
            author=author,
            target=target_text
        )

        gif = await self.get_gif(
            animation["endpoint"]
        )

        embed = discord.Embed(
            description=text,
            color=ANIMATION_COLOR
        )

        if gif:

            embed.set_image(
                url=gif
            )

        embed.set_footer(
            text="Animación • Band Arg"
        )

        try:

            await ctx.send(
                embed=embed
            )

        except discord.Forbidden:

            try:

                await ctx.send(
                    text
                )

            except Exception:
                pass

        except Exception as e:

            print(
                f"[ANIMACIONES] Error enviando "
                f"animación: {e}"
            )

    # ========================================================
    # HUG
    # ========================================================

    @commands.hybrid_command(
        name="hug",
        description="Abraza a otro usuario."
    )
    async def hug(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "hug",
            usuario
        )

    # ========================================================
    # KISS
    # ========================================================

    @commands.hybrid_command(
        name="kiss",
        description="Dale un beso a otro usuario."
    )
    async def kiss(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "kiss",
            usuario
        )

    # ========================================================
    # PAT
    # ========================================================

    @commands.hybrid_command(
        name="pat",
        description="Acaricia a otro usuario."
    )
    async def pat(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "pat",
            usuario
        )

    # ========================================================
    # CUDDLE
    # ========================================================

    @commands.hybrid_command(
        name="cuddle",
        description="Acurrúcate con otro usuario."
    )
    async def cuddle(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "cuddle",
            usuario
        )

    # ========================================================
    # POKE
    # ========================================================

    @commands.hybrid_command(
        name="poke",
        description="Hazle poke a otro usuario."
    )
    async def poke(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "poke",
            usuario
        )

    # ========================================================
    # HIGHFIVE
    # ========================================================

    @commands.hybrid_command(
        name="highfive",
        description="Choca los cinco con otro usuario."
    )
    async def highfive(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "highfive",
            usuario
        )

    # ========================================================
    # BITE
    # ========================================================

    @commands.hybrid_command(
        name="bite",
        description="Muerde a otro usuario."
    )
    async def bite(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "bite",
            usuario
        )

    # ========================================================
    # SLAP
    # ========================================================

    @commands.hybrid_command(
        name="slap",
        description="Dale una cachetada a otro usuario."
    )
    async def slap(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "slap",
            usuario
        )

    # ========================================================
    # PUNCH
    # ========================================================

    @commands.hybrid_command(
        name="punch",
        description="Dale un puñetazo a otro usuario."
    )
    async def punch(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "punch",
            usuario
        )

    # ========================================================
    # KICK ANIMACIÓN
    #
    # IMPORTANTE:
    # NO usamos "kick" porque ya existe tu comando
    # de moderación /kick.
    #
    # Ahora:
    # s!akick @usuario
    # /akick @usuario
    # ========================================================

    @commands.hybrid_command(
        name="akick",
        description="Dale una patada animada a otro usuario."
    )
    async def akick(
        self,
        ctx,
        usuario: discord.Member
    ):

        await self.do_animation(
            ctx,
            "kick",
            usuario
        )

    # ========================================================
    # WAVE
    # ========================================================

    @commands.hybrid_command(
        name="wave",
        description="Saluda."
    )
    async def wave(
        self,
        ctx
    ):

        await self.do_animation(
            ctx,
            "wave"
        )

    # ========================================================
    # DANCE
    # ========================================================

    @commands.hybrid_command(
        name="dance",
        description="Baila."
    )
    async def dance(
        self,
        ctx
    ):

        await self.do_animation(
            ctx,
            "dance"
        )

    # ========================================================
    # CRY
    # ========================================================

    @commands.hybrid_command(
        name="cry",
        description="Llora."
    )
    async def cry(
        self,
        ctx
    ):

        await self.do_animation(
            ctx,
            "cry"
        )

    # ========================================================
    # HAPPY
    # ========================================================

    @commands.hybrid_command(
        name="happy",
        description="Muestra felicidad."
    )
    async def happy(
        self,
        ctx
    ):

        await self.do_animation(
            ctx,
            "happy"
        )

    # ========================================================
    # ANGRY
    # ========================================================

    @commands.hybrid_command(
        name="angry",
        description="Muestra enojo."
    )
    async def angry(
        self,
        ctx
    ):

        await self.do_animation(
            ctx,
            "angry"
        )

    # ========================================================
    # BLUSH
    # ========================================================

    @commands.hybrid_command(
        name="blush",
        description="Se pone rojo/a."
    )
    async def blush(
        self,
        ctx
    ):

        await self.do_animation(
            ctx,
            "blush"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Animaciones(bot)
    )