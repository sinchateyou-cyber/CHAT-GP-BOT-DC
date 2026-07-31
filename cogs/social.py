import random
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# GIFS DE CADA ACCIÓN
# ============================================================
GIFS = {
    "abrazo": [
        "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
        "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
        "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
    ],
    "beso": [
        "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
        "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
        "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
    ],
    "acariciar": [
        "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
        "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
        "https://media.giphy.com/media/ye7OTQgynvhb2/giphy.gif",
    ],
    "cachetada": [
        "https://media.giphy.com/media/Zau0yrl17uzdK/giphy.gif",
        "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
        "https://media.giphy.com/media/3XlEk2RxPS1m8/giphy.gif",
    ],
    "morder": [
        "https://media.giphy.com/media/8rEiN2GsOdQTm/giphy.gif",
        "https://media.giphy.com/media/10kofq1GQJ9lZK/giphy.gif",
        "https://media.giphy.com/media/3o7TKwmnDgQb5jemjK/giphy.gif",
    ],
    "cosquillas": [
        "https://media.giphy.com/media/4NrWuucrAOu0U/giphy.gif",
        "https://media.giphy.com/media/10BH7dPjipwQJ2/giphy.gif",
        "https://media.giphy.com/media/xT0xeuOy2Fcl9vDGiA/giphy.gif",
    ],
    "saludar": [
        "https://media.giphy.com/media/ASd0Ukj0y3qMM/giphy.gif",
        "https://media.giphy.com/media/3o6ZtaO9BZHcOjmErm/giphy.gif",
        "https://media.giphy.com/media/7DzlajZNYL4Zq/giphy.gif",
    ],
    "highfive": [
        "https://media.giphy.com/media/5OqXb948EBkyU/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
        "https://media.giphy.com/media/3oEjHV0z8S7WM4MwnK/giphy.gif",
    ],
    "guiño": [
        "https://media.giphy.com/media/3o7TKC3d5X5bK3K6gE/giphy.gif",
        "https://media.giphy.com/media/26BRv0ThflsHCqDrG/giphy.gif",
        "https://media.giphy.com/media/6ra84Uso2hoir3YCgb/giphy.gif",
    ],
    "pat": [
        "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
        "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
        "https://media.giphy.com/media/ye7OTQgynvhb2/giphy.gif",
    ],
}
# ============================================================
# MENSAJES
# ============================================================
MENSAJES = {
    "abrazo": [
        "🤗 {autor} le dio un abrazo a {usuario}.",
        "🫂 {autor} abrazó a {usuario} con mucho cariño.",
        "💖 {autor} le dio un enorme abrazo a {usuario}.",
    ],
    "beso": [
        "💋 {autor} le dio un beso a {usuario}.",
        "😘 {autor} le mandó un besito a {usuario}.",
        "💕 {autor} le dio un tierno beso a {usuario}.",
    ],
    "acariciar": [
        "🥰 {autor} acarició a {usuario}.",
        "🫶 {autor} le dio unas caricias a {usuario}.",
        "💖 {autor} acarició suavemente a {usuario}.",
    ],
    "cachetada": [
        "👋 {autor} le dio una cachetada a {usuario}.",
        "💥 ¡PUM! {autor} le dio una cachetada a {usuario}.",
        "😳 {autor} le pegó una cachetada a {usuario}.",
    ],
    "morder": [
        "🦷 {autor} mordió a {usuario}.",
        "😈 {autor} decidió morder a {usuario}.",
        "🩸 ¡Auch! {autor} mordió a {usuario}.",
    ],
    "cosquillas": [
        "😂 {autor} le hizo cosquillas a {usuario}.",
        "🤣 {usuario} no puede parar de reír por culpa de {autor}.",
        "😆 {autor} atacó a {usuario} con cosquillas.",
    ],
    "saludar": [
        "👋 {autor} saludó a {usuario}.",
        "😊 {autor} le dijo hola a {usuario}.",
        "✨ {autor} pasó a saludar a {usuario}.",
    ],
    "highfive": [
        "✋ {autor} chocó los cinco con {usuario}.",
        "🙌 ¡High five! {autor} y {usuario}.",
        "🤝 {autor} y {usuario} hicieron un high five.",
    ],
    "guiño": [
        "😉 {autor} le guiñó el ojo a {usuario}.",
        "😏 {autor} le hizo un guiño a {usuario}.",
        "✨ {autor} le lanzó un guiño a {usuario}.",
    ],
    "pat": [
        "🫳 {autor} le dio unas palmaditas a {usuario}.",
        "🥺 {autor} le hizo pat pat a {usuario}.",
        "💖 {autor} le dio un cariñoso pat pat a {usuario}.",
    ],
}
# ============================================================
# COLORES
# ============================================================
COLORES = {
    "abrazo": discord.Colour.pink(),
    "beso": discord.Colour.red(),
    "acariciar": discord.Colour.purple(),
    "cachetada": discord.Colour.orange(),
    "morder": discord.Colour.dark_red(),
    "cosquillas": discord.Colour.gold(),
    "saludar": discord.Colour.green(),
    "highfive": discord.Colour.blue(),
    "guiño": discord.Colour.magenta(),
    "pat": discord.Colour.blurple(),
}
# ============================================================
# COG SOCIAL
# ============================================================
class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ========================================================
    # FUNCIÓN PRINCIPAL
    # ========================================================
    async def accion_social(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        accion: str
    ):
        # ----------------------------------------------------
        # NO PERMITIR USARSE A UNO MISMO
        # ----------------------------------------------------
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                f"😅 No podés usar "
                f"**/{accion}** con vos mismo.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # MENSAJE ALEATORIO
        # ----------------------------------------------------
        mensaje = random.choice(
            MENSAJES[accion]
        ).format(
            autor=interaction.user.mention,
            usuario=usuario.mention
        )
        # ----------------------------------------------------
        # GIF ALEATORIO
        # ----------------------------------------------------
        gif = random.choice(
            GIFS[accion]
        )
        # ----------------------------------------------------
        # CREAR EMBED
        # ----------------------------------------------------
        embed = discord.Embed(
            description=mensaje,
            colour=COLORES.get(
                accion,
                discord.Colour.blurple()
            )
        )
        # ----------------------------------------------------
        # COLOCAR GIF
        # ----------------------------------------------------
        embed.set_image(
            url=gif
        )
        # ----------------------------------------------------
        # AVATAR
        # ----------------------------------------------------
        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )
        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------
        embed.set_footer(
            text=(
                f"Acción realizada por "
                f"{interaction.user.display_name}"
            )
        )
        # ----------------------------------------------------
        # ENVIAR
        # ----------------------------------------------------
        await interaction.response.send_message(
            content=(
                f"{interaction.user.mention} "
                f"{usuario.mention}"
            ),
            embed=embed
        )
    # ========================================================
    # /ABRAZO
    # ========================================================
    @app_commands.command(
        name="abrazo",
        description="Dale un abrazo a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés abrazar."
    )
    async def abrazo(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "abrazo"
        )
    # ========================================================
    # /BESO
    # ========================================================
    @app_commands.command(
        name="beso",
        description="Dale un beso a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés dar un beso."
    )
    async def beso(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "beso"
        )
    # ========================================================
    # /ACARICIAR
    # ========================================================
    @app_commands.command(
        name="acariciar",
        description="Acaricia a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés acariciar."
    )
    async def acariciar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "acariciar"
        )
    # ========================================================
    # /CACHETADA
    # ========================================================
    @app_commands.command(
        name="cachetada",
        description="Dale una cachetada a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés dar una cachetada."
    )
    async def cachetada(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "cachetada"
        )
    # ========================================================
    # /MORDER
    # ========================================================
    @app_commands.command(
        name="morder",
        description="Muerde a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés morder."
    )
    async def morder(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "morder"
        )
    # ========================================================
    # /COSQUILLAS
    # ========================================================
    @app_commands.command(
        name="cosquillas",
        description="Hazle cosquillas a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés hacer cosquillas."
    )
    async def cosquillas(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "cosquillas"
        )
    # ========================================================
    # /SALUDAR
    # ========================================================
    @app_commands.command(
        name="saludar",
        description="Saluda a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés saludar."
    )
    async def saludar(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "saludar"
        )
    # ========================================================
    # /HIGHFIVE
    # ========================================================
    @app_commands.command(
        name="highfive",
        description="Choca los cinco con otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario con el que querés hacer high five."
    )
    async def highfive(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "highfive"
        )
    # ========================================================
    # /GUIÑO
    # ========================================================
    @app_commands.command(
        name="guiño",
        description="Guiñale el ojo a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés guiñar."
    )
    async def guino(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "guiño"
        )
    # ========================================================
    # /PAT
    # ========================================================
    @app_commands.command(
        name="pat",
        description="Dale unas palmaditas a otro usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés hacerle pat pat."
    )
    async def pat(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        await self.accion_social(
            interaction,
            usuario,
            "pat"
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Social(bot)
    )
    print(
        "✅ Sistema social con GIFs "
        "cargado correctamente"
    )