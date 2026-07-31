import random
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# FRASES DE RESPUESTA
# ============================================================
RESPUESTAS = {
    "abrazo": [
        "🤗 {autor} le dio un abrazo enorme a {usuario}.",
        "🫂 {autor} abrazó a {usuario} con mucho cariño.",
        "💖 {autor} y {usuario} se dieron un lindo abrazo.",
    ],
    "beso": [
        "💋 {autor} le dio un beso a {usuario}.",
        "😘 {autor} le mandó un besito a {usuario}.",
        "💕 {autor} le dio un tierno beso a {usuario}.",
    ],
    "acariciar": [
        "🥰 {autor} acarició suavemente a {usuario}.",
        "💖 {autor} le dio unas caricias a {usuario}.",
        "🫶 {autor} acarició a {usuario} con mucho cariño.",
    ],
    "cachetada": [
        "👋 {autor} le dio una cachetada a {usuario}.",
        "😳 ¡PUM! {autor} le dio una cachetada a {usuario}.",
        "💥 {autor} le pegó una cachetada a {usuario}.",
    ],
    "morder": [
        "🦷 {autor} mordió a {usuario}.",
        "😈 {autor} decidió morder a {usuario}.",
        "🩸 ¡Auch! {autor} mordió a {usuario}.",
    ],
    "cosquillas": [
        "😂 {autor} le hizo cosquillas a {usuario}.",
        "🤣 {usuario} no puede parar de reír por las cosquillas de {autor}.",
        "😆 {autor} atacó a {usuario} con cosquillas.",
    ],
    "saludar": [
        "👋 {autor} saludó a {usuario}.",
        "😊 {autor} le dijo hola a {usuario}.",
        "✨ ¡Hola! {autor} saludó a {usuario}.",
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
        "🫳 {autor} le dio unas palmaditas en la cabeza a {usuario}.",
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
    # FUNCIÓN PARA CREAR EMBEDS
    # ========================================================
    async def accion_social(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        accion: str
    ):
        # ----------------------------------------------------
        # EVITAR HACER LA ACCIÓN SOBRE UNO MISMO
        # ----------------------------------------------------
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                f"😅 No podés usar **/{accion}** "
                f"con vos mismo.",
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # OBTENER MENSAJE ALEATORIO
        # ----------------------------------------------------
        mensaje = random.choice(
            RESPUESTAS[accion]
        ).format(
            autor=interaction.user.mention,
            usuario=usuario.mention
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
        # AVATAR DEL USUARIO
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
        "✅ Sistema social cargado correctamente"
    )