import random
import discord

from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

MAX_PUNTOS = 15


# ============================================================
# BARAJA ESPAÑOLA DE 40
# ============================================================

PALOS = {
    "espadas": "⚔️",
    "bastos": "🪵",
    "oros": "🪙",
    "copas": "🍷",
}

NUMEROS = [
    1, 2, 3, 4, 5, 6, 7, 10, 11, 12
]

NOMBRES = {
    1: "As",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    10: "Sota",
    11: "Caballo",
    12: "Rey",
}


# ============================================================
# JERARQUÍA REAL DEL TRUCO ARGENTINO
# ============================================================

FUERZA = {
    (1, "espadas"): 14,
    (1, "bastos"): 13,
    (7, "espadas"): 12,
    (7, "oros"): 11,

    (3, "espadas"): 10,
    (3, "bastos"): 10,
    (3, "oros"): 10,
    (3, "copas"): 10,

    (2, "espadas"): 9,
    (2, "bastos"): 9,
    (2, "oros"): 9,
    (2, "copas"): 9,

    (1, "oros"): 8,
    (1, "copas"): 8,

    (12, "espadas"): 7,
    (12, "bastos"): 7,
    (12, "oros"): 7,
    (12, "copas"): 7,

    (11, "espadas"): 6,
    (11, "bastos"): 6,
    (11, "oros"): 6,
    (11, "copas"): 6,

    (10, "espadas"): 5,
    (10, "bastos"): 5,
    (10, "oros"): 5,
    (10, "copas"): 5,

    (7, "bastos"): 4,
    (7, "copas"): 4,

    (6, "espadas"): 3,
    (6, "bastos"): 3,
    (6, "oros"): 3,
    (6, "copas"): 3,

    (5, "espadas"): 2,
    (5, "bastos"): 2,
    (5, "oros"): 2,
    (5, "copas"): 2,

    (4, "espadas"): 1,
    (4, "bastos"): 1,
    (4, "oros"): 1,
    (4, "copas"): 1,
}


# ============================================================
# CARTA
# ============================================================

class Carta:

    def __init__(self, numero, palo):
        self.numero = numero
        self.palo = palo

    @property
    def fuerza(self):
        return FUERZA[(self.numero, self.palo)]

    @property
    def nombre(self):
        return NOMBRES[self.numero]

    def mostrar(self):
        return (
            f"{PALOS[self.palo]} "
            f"{self.nombre} de {self.palo.capitalize()}"
        )


# ============================================================
# CREAR BARAJA
# ============================================================

def crear_baraja():

    baraja = []

    for palo in PALOS:

        for numero in NUMEROS:

            baraja.append(
                Carta(
                    numero,
                    palo
                )
            )

    return baraja


# ============================================================
# VALOR ENVIDO
# ============================================================

def valor_envido(carta):

    if carta.numero >= 10:
        return 0

    return carta.numero


def calcular_envido(mano):

    mejores = 0

    for palo in PALOS:

        cartas = [
            carta
            for carta in mano
            if carta.palo == palo
        ]

        if len(cartas) >= 2:

            valores = sorted(
                [
                    valor_envido(carta)
                    for carta in cartas
                ],
                reverse=True
            )

            total = (
                20
                + valores[0]
                + valores[1]
            )

            mejores = max(
                mejores,
                total
            )

    if mejores == 0:

        mejores = max(
            valor_envido(carta)
            for carta in mano
        )

    return mejores


# ============================================================
# FLOR
# ============================================================

def tiene_flor(mano):

    if len(mano) != 3:
        return False

    return (
        mano[0].palo
        == mano[1].palo
        == mano[2].palo
    )


def valor_flor(mano):

    if not tiene_flor(mano):
        return 0

    return (
        20
        + sum(
            valor_envido(carta)
            for carta in mano
        )
    )


# ============================================================
# PARTIDA
# ============================================================

class Partida:

    def __init__(self, jugador):

        self.jugador = jugador

        self.baraja = crear_baraja()
        random.shuffle(self.baraja)

        self.mano_jugador = []
        self.mano_bot = []

        self.puntos_jugador = 0
        self.puntos_bot = 0

        self.bazas_jugador = 0
        self.bazas_bot = 0

        self.baza_actual = 1

        self.turno = "jugador"

        self.ultima_jugada_jugador = None
        self.ultima_jugada_bot = None

        self.resultados_bazas = []

        # ----------------------------
        # Truco
        # ----------------------------

        self.truco_nivel = 1

        self.truco_pedido_por = None

        self.esperando_respuesta_truco = False

        # ----------------------------
        # Envido
        # ----------------------------

        self.envido_pedido = False

        self.envido_tipo = None

        self.envido_resuelto = False

        # ----------------------------
        # Flor
        # ----------------------------

        self.flor_jugador = False
        self.flor_bot = False

        self.terminada = False

        self.repartir()

    # ========================================================
    # REPARTIR
    # ========================================================

    def repartir(self):

        self.mano_jugador = []
        self.mano_bot = []

        for _ in range(3):

            self.mano_jugador.append(
                self.baraja.pop()
            )

            self.mano_bot.append(
                self.baraja.pop()
            )

        self.flor_jugador = tiene_flor(
            self.mano_jugador
        )

        self.flor_bot = tiene_flor(
            self.mano_bot
        )

    # ========================================================
    # CARTAS
    # ========================================================

    def cartas_jugador_texto(self):

        texto = ""

        for i, carta in enumerate(
            self.mano_jugador,
            1
        ):

            texto += (
                f"**{i}️⃣** {carta.mostrar()}\n"
            )

        return texto

    # ========================================================
    # FUERZA
    # ========================================================

    def ganador_carta(
        self,
        carta_jugador,
        carta_bot
    ):

        if carta_jugador.fuerza > carta_bot.fuerza:
            return "jugador"

        if carta_bot.fuerza > carta_jugador.fuerza:
            return "bot"

        return "empate"

    # ========================================================
    # JUGAR CARTA
    # ========================================================

    def jugar_jugador(self, indice):

        if indice < 0:
            return None

        if indice >= len(
            self.mano_jugador
        ):
            return None

        return self.mano_jugador.pop(
            indice
        )

    # ========================================================
    # IA BOT
    # ========================================================

    def elegir_carta_bot(self):

        if not self.mano_bot:
            return None

        # Si el jugador acaba de tirar,
        # intentamos ganar usando la carta
        # más barata que pueda hacerlo.

        if self.ultima_jugada_jugador:

            objetivo = (
                self.ultima_jugada_jugador
            )

            posibles = [
                carta
                for carta in self.mano_bot
                if carta.fuerza > objetivo.fuerza
            ]

            if posibles:

                carta = min(
                    posibles,
                    key=lambda c: c.fuerza
                )

                self.mano_bot.remove(carta)

                return carta

        # Si no puede ganar,
        # tira la carta más débil.

        carta = min(
            self.mano_bot,
            key=lambda c: c.fuerza
        )

        self.mano_bot.remove(carta)

        return carta

    # ========================================================
    # FUERZA DE MANO
    # ========================================================

    def fuerza_mano_bot(self):

        return sum(
            carta.fuerza
            for carta in self.mano_bot
        )

    # ========================================================
    # IA TRUCO
    # ========================================================

    def bot_quiere_cantar_truco(self):

        fuerza = self.fuerza_mano_bot()

        return fuerza >= 24

    def bot_acepta_truco(self):

        fuerza = self.fuerza_mano_bot()

        probabilidad = min(
            0.95,
            0.35 + fuerza / 60
        )

        return random.random() < probabilidad

    # ========================================================
    # CANTAR TRUCO
    # ========================================================

    def cantar_truco(self, jugador):

        if self.truco_nivel >= 4:
            return False

        self.truco_pedido_por = jugador

        self.esperando_respuesta_truco = True

        return True

    # ========================================================
    # SUBIR TRUCO
    # ========================================================

    def subir_truco(self):

        if self.truco_nivel >= 4:
            return False

        self.truco_nivel += 1

        self.esperando_respuesta_truco = True

        return True

    # ========================================================
    # NOMBRE DEL TRUCO
    # ========================================================

    def nombre_truco(self):

        nombres = {
            1: "Nada",
            2: "Truco",
            3: "Retruco",
            4: "Vale 4"
        }

        return nombres[
            self.truco_nivel
        ]

    # ========================================================
    # PUNTOS SI NO QUIERO
    # ========================================================

    def puntos_no_quiero(self):

        if self.truco_nivel == 2:
            return 1

        if self.truco_nivel == 3:
            return 2

        if self.truco_nivel == 4:
            return 3

        return 1

    # ========================================================
    # RESOLVER BAZA
    # ========================================================

    def resolver_baza(self):

        jugador = (
            self.ultima_jugada_jugador
        )

        bot = (
            self.ultima_jugada_bot
        )

        if not jugador or not bot:
            return None

        ganador = self.ganador_carta(
            jugador,
            bot
        )

        if ganador == "jugador":

            self.bazas_jugador += 1

        elif ganador == "bot":

            self.bazas_bot += 1

        self.resultados_bazas.append(
            ganador
        )

        return ganador

    # ========================================================
    # GANADOR DE LA MANO
    # ========================================================

    def ganador_mano(self):

        if self.bazas_jugador >= 2:
            return "jugador"

        if self.bazas_bot >= 2:
            return "bot"

        # Si termina la tercera baza

        if self.baza_actual > 3:

            if self.bazas_jugador > self.bazas_bot:
                return "jugador"

            if self.bazas_bot > self.bazas_jugador:
                return "bot"

            # En empate, gana quien ganó
            # la primera baza.

            for resultado in self.resultados_bazas:

                if resultado != "empate":
                    return resultado

            return "jugador"

        return None

    # ========================================================
    # PUNTUACIÓN
    # ========================================================

    def dar_puntos(self, ganador, puntos=None):

        if puntos is None:
            puntos = self.truco_nivel

        if ganador == "jugador":

            self.puntos_jugador += puntos

        else:

            self.puntos_bot += puntos

    # ========================================================
    # TERMINÓ PARTIDA
    # ========================================================

    def comprobar_final(self):

        if self.puntos_jugador >= MAX_PUNTOS:

            self.terminada = True
            return "jugador"

        if self.puntos_bot >= MAX_PUNTOS:

            self.terminada = True
            return "bot"

        return None


# ============================================================
# VIEW
# ============================================================

class TrucoView(
    discord.ui.View
):

    def __init__(
        self,
        partida,
        cog
    ):

        super().__init__(
            timeout=600
        )

        self.partida = partida
        self.cog = cog

        self.crear_botones()

    # ========================================================
    # COMPROBAR USUARIO
    # ========================================================

    async def interaction_check(
        self,
        interaction
    ):

        if (
            interaction.user.id
            != self.partida.jugador.id
        ):

            await interaction.response.send_message(
                "❌ Esta partida no es tuya, maestro.",
                ephemeral=True
            )

            return False

        return True

    # ========================================================
    # CREAR BOTONES
    # ========================================================

    def crear_botones(self):

        self.clear_items()

        # ----------------------------------------------------
        # CARTAS
        # ----------------------------------------------------

        for indice, carta in enumerate(
            self.partida.mano_jugador
        ):

            boton = discord.ui.Button(
                label=(
                    f"{indice + 1} - "
                    f"{carta.nombre}"
                ),
                emoji=carta.mostrar().split()[0],
                style=discord.ButtonStyle.primary,
                row=0
            )

            async def callback(
                interaction,
                i=indice
            ):

                await self.jugar_carta(
                    interaction,
                    i
                )

            boton.callback = callback

            self.add_item(
                boton
            )

        # ----------------------------------------------------
        # TRUCO
        # ----------------------------------------------------

        if self.partida.truco_nivel < 4:

            nombre = {
                1: "Truco",
                2: "Retruco",
                3: "Vale 4"
            }[
                self.partida.truco_nivel
            ]

            boton = discord.ui.Button(
                label=nombre,
                emoji="🔥",
                style=discord.ButtonStyle.danger,
                row=1
            )

            boton.callback = (
                self.truco_callback
            )

            self.add_item(
                boton
            )

        # ----------------------------------------------------
        # ENVIDO
        # ----------------------------------------------------

        if not self.partida.envido_pedido:

            boton = discord.ui.Button(
                label="Envido",
                emoji="🪙",
                style=discord.ButtonStyle.success,
                row=1
            )

            boton.callback = (
                self.envido_callback
            )

            self.add_item(
                boton
            )

        # ----------------------------------------------------
        # FLOR
        # ----------------------------------------------------

        if (
            self.partida.flor_jugador
            and not self.partida.envido_resuelto
        ):

            boton = discord.ui.Button(
                label="Flor",
                emoji="🌹",
                style=discord.ButtonStyle.success,
                row=2
            )

            boton.callback = (
                self.flor_callback
            )

            self.add_item(
                boton
            )

    # ========================================================
    # JUGAR CARTA
    # ========================================================

    async def jugar_carta(
        self,
        interaction,
        indice
    ):

        if self.partida.esperando_respuesta_truco:

            return await interaction.response.send_message(
                "🔥 Primero tenés que resolver el Truco.",
                ephemeral=True
            )

        carta_jugador = (
            self.partida.jugar_jugador(
                indice
            )
        )

        if carta_jugador is None:

            return await interaction.response.send_message(
                "❌ Esa carta no existe.",
                ephemeral=True
            )

        self.partida.ultima_jugada_jugador = (
            carta_jugador
        )

        # ----------------------------------------------------
        # BOT
        # ----------------------------------------------------

        carta_bot = (
            self.partida.elegir_carta_bot()
        )

        self.partida.ultima_jugada_bot = (
            carta_bot
        )

        ganador = (
            self.partida.resolver_baza()
        )

        resultado = {
            "jugador":
                "🟢 Ganaste la baza, ¡bien ahí!",
            "bot":
                "🔴 El bot ganó la baza.",
            "empate":
                "⚪ Parda."
        }.get(
            ganador,
            "❓"
        )

        # ----------------------------------------------------
        # COMPROBAR MANO
        # ----------------------------------------------------

        ganador_mano = (
            self.partida.ganador_mano()
        )

        if ganador_mano:

            self.partida.dar_puntos(
                ganador_mano
            )

            ganador_partida = (
                self.partida.comprobar_final()
            )

            if ganador_partida:

                await self.finalizar_partida(
                    interaction,
                    ganador_partida,
                    carta_jugador,
                    carta_bot,
                    resultado
                )

                return

            # Nueva mano

            self.partida.baraja = crear_baraja()

            random.shuffle(
                self.partida.baraja
            )

            self.partida.repartir()

            self.partida.bazas_jugador = 0
            self.partida.bazas_bot = 0
            self.partida.baza_actual = 1
            self.partida.resultados_bazas = []

            self.partida.ultima_jugada_jugador = None
            self.partida.ultima_jugada_bot = None

            self.partida.truco_nivel = 1
            self.partida.truco_pedido_por = None
            self.partida.esperando_respuesta_truco = False

            self.partida.envido_pedido = False
            self.partida.envido_resuelto = False

            self.crear_botones()

            embed = self.cog.crear_embed(
                self.partida
            )

            embed.add_field(
                name="🏆 Mano anterior",
                value=(
                    f"{resultado}\n\n"
                    f"🧑 Vos ganaste la mano."
                ),
                inline=False
            )

            await interaction.response.edit_message(
                embed=embed,
                view=self
            )

            return

        # ----------------------------------------------------
        # SIGUIENTE BAZA
        # ----------------------------------------------------

        self.partida.baza_actual += 1

        self.partida.ultima_jugada_jugador = None
        self.partida.ultima_jugada_bot = None

        self.crear_botones()

        embed = self.cog.crear_embed(
            self.partida
        )

        embed.add_field(
            name="⚔️ Última baza",
            value=(
                f"🧑 {carta_jugador.mostrar()}\n"
                f"🤖 {carta_bot.mostrar()}\n\n"
                f"{resultado}"
            ),
            inline=False
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )

    # ========================================================
    # TRUCO
    # ========================================================

    async def truco_callback(
        self,
        interaction
    ):

        if self.partida.truco_nivel >= 4:

            return await interaction.response.send_message(
                "❌ Ya están en Vale 4.",
                ephemeral=True
            )

        self.partida.truco_nivel += 1

        self.partida.truco_pedido_por = "jugador"

        # ----------------------------------------------------
        # RESPUESTA IA
        # ----------------------------------------------------

        acepta = (
            self.partida.bot_acepta_truco()
        )

        if not acepta:

            puntos = (
                self.partida.puntos_no_quiero()
            )

            self.partida.puntos_bot += puntos

            await interaction.response.send_message(
                f"🤖 **¡NO QUIERO!**\n"
                f"El bot se achicó.\n"
                f"🪙 Ganás **{puntos} punto(s)**.",
                ephemeral=False
            )

            self.partida.esperando_respuesta_truco = False

            return

        nombre = (
            self.partida.nombre_truco()
        )

        self.partida.esperando_respuesta_truco = False

        self.crear_botones()

        await interaction.response.edit_message(
            embed=self.cog.crear_embed(
                self.partida,
                mensaje=f"🔥 **¡{nombre.upper()}!**\n"
                        f"🤖 El bot dijo: **¡QUIERO!**"
            ),
            view=self
        )

    # ========================================================
    # ENVIDO
    # ========================================================

    async def envido_callback(
        self,
        interaction
    ):

        if self.partida.envido_pedido:

            return await interaction.response.send_message(
                "❌ Ya se cantó el Envido.",
                ephemeral=True
            )

        self.partida.envido_pedido = True

        jugador = calcular_envido(
            self.partida.mano_jugador
        )

        bot = calcular_envido(
            self.partida.mano_bot
        )

        # IA
        acepta = (
            random.random() < 0.75
        )

        if not acepta:

            self.partida.puntos_jugador += 1

            mensaje = (
                "🪙 **¡ENVIDO!**\n\n"
                "🤖 Bot: **NO QUIERO**.\n"
                "🧑 Ganás **1 punto**."
            )

        else:

            if jugador > bot:

                self.partida.puntos_jugador += 2

                mensaje = (
                    "🪙 **¡ENVIDO!**\n\n"
                    f"🧑 Vos: **{jugador}**\n"
                    f"🤖 Bot: **{bot}**\n\n"
                    "🟢 **GANASTE EL ENVIDO!**\n"
                    "🪙 +2 puntos."
                )

            elif bot > jugador:

                self.partida.puntos_bot += 2

                mensaje = (
                    "🪙 **¡ENVIDO!**\n\n"
                    f"🧑 Vos: **{jugador}**\n"
                    f"🤖 Bot: **{bot}**\n\n"
                    "🔴 **EL BOT GANÓ EL ENVIDO.**\n"
                    "🪙 +2 puntos para el bot."
                )

            else:

                mensaje = (
                    "🪙 **¡ENVIDO!**\n\n"
                    f"🧑 Vos: **{jugador}**\n"
                    f"🤖 Bot: **{bot}**\n\n"
                    "⚪ **EMPATE.**"
                )

        self.partida.envido_resuelto = True

        self.crear_botones()

        await interaction.response.edit_message(
            embed=self.cog.crear_embed(
                self.partida,
                mensaje=mensaje
            ),
            view=self
        )

    # ========================================================
    # FLOR
    # ========================================================

    async def flor_callback(
        self,
        interaction
    ):

        if not self.partida.flor_jugador:

            return await interaction.response.send_message(
                "❌ No tenés flor.",
                ephemeral=True
            )

        jugador = valor_flor(
            self.partida.mano_jugador
        )

        bot = valor_flor(
            self.partida.mano_bot
        )

        if not self.partida.flor_bot:

            self.partida.puntos_jugador += 3

            mensaje = (
                "🌹 **¡FLOR!**\n\n"
                "🤖 El bot no tiene flor.\n"
                "🧑 Ganás **3 puntos**."
            )

        elif jugador > bot:

            self.partida.puntos_jugador += 3

            mensaje = (
                "🌹 **¡FLOR!**\n\n"
                f"🧑 Tu flor: **{jugador}**\n"
                f"🤖 Flor del bot: **{bot}**\n\n"
                "🟢 **GANASTE LA FLOR!**"
            )

        elif bot > jugador:

            self.partida.puntos_bot += 3

            mensaje = (
                "🌹 **¡FLOR!**\n\n"
                f"🧑 Tu flor: **{jugador}**\n"
                f"🤖 Flor del bot: **{bot}**\n\n"
                "🔴 **EL BOT GANÓ LA FLOR.**"
            )

        else:

            mensaje = (
                "🌹 **FLOR EMPATADA.**"
            )

        self.partida.envido_resuelto = True

        self.crear_botones()

        await interaction.response.edit_message(
            embed=self.cog.crear_embed(
                self.partida,
                mensaje=mensaje
            ),
            view=self
        )

    # ========================================================
    # FINAL PARTIDA
    # ========================================================

    async def finalizar_partida(
        self,
        interaction,
        ganador,
        carta_jugador,
        carta_bot,
        resultado
    ):

        self.partida.terminada = True

        self.clear_items()

        if ganador == "jugador":

            titulo = (
                "🏆🇦🇷 ¡GANASTE EL TRUCO!"
            )

        else:

            titulo = (
                "🤖🏆 EL BOT GANÓ EL TRUCO"
            )

        embed = self.cog.crear_embed(
            self.partida
        )

        embed.add_field(
            name="🏆 RESULTADO FINAL",
            value=(
                f"{titulo}\n\n"
                f"🧑 {carta_jugador.mostrar()}\n"
                f"🤖 {carta_bot.mostrar()}\n\n"
                f"{resultado}"
            ),
            inline=False
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ============================================================
# COG
# ============================================================

class Truco(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.partidas = {}

    # ========================================================
    # EMBED
    # ========================================================

    def crear_embed(
        self,
        partida,
        mensaje=None
    ):

        embed = discord.Embed(
            title="🇦🇷 🃏 TRUCO ARGENTINO",
            description=(
                "━━━━━━━━━━━━━━━━━━━━\n"
                "⚔️ **PARTIDA 1 VS 1**\n"
                "━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.add_field(
            name="👤 Vos",
            value=(
                f"🏆 **{partida.puntos_jugador}** puntos\n\n"
                f"{partida.cartas_jugador_texto()}"
            ),
            inline=True
        )

        embed.add_field(
            name="🤖 Bot",
            value=(
                f"🏆 **{partida.puntos_bot}** puntos\n"
                f"⚔️ Bazas: {partida.bazas_bot}"
            ),
            inline=True
        )

        embed.add_field(
            name="🔥 Truco",
            value=(
                f"**{partida.nombre_truco()}**\n"
                f"🪙 Vale: **{partida.truco_nivel}**"
            ),
            inline=False
        )

        embed.add_field(
            name="⚔️ Bazas",
            value=(
                f"👤 Vos: **{partida.bazas_jugador}**\n"
                f"🤖 Bot: **{partida.bazas_bot}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🎴 Baza",
            value=(
                f"**{partida.baza_actual}/3**"
            ),
            inline=True
        )

        if mensaje:

            embed.add_field(
                name="📢 Mesa",
                value=mensaje,
                inline=False
            )

        embed.set_footer(
            text="Primero en llegar a 15 puntos gana 🇦🇷"
        )

        return embed

    # ========================================================
    # /TRUCO
    # ========================================================

    @app_commands.command(
        name="truco",
        description="Jugá al Truco argentino contra el bot."
    )
    async def truco(
        self,
        interaction: discord.Interaction
    ):

        usuario_id = interaction.user.id

        partida_actual = (
            self.partidas.get(
                usuario_id
            )
        )

        if (
            partida_actual
            and not partida_actual.terminada
        ):

            return await interaction.response.send_message(
                "❌ Ya tenés una partida activa.\n"
                "Terminá esa primero, máquina.",
                ephemeral=True
            )

        partida = Partida(
            interaction.user
        )

        self.partidas[
            usuario_id
        ] = partida

        view = TrucoView(
            partida,
            self
        )

        embed = self.crear_embed(
            partida,
            mensaje=(
                "🃏 **¡Repartidas!**\n"
                "Arrancás vos.\n\n"
                "¿Qué vas a hacer, maestro?"
            )
        )

        await interaction.response.send_message(
            embed=embed,
            view=view
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Truco(bot)
    )