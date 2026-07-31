import discord
from discord import app_commands
from discord.ext import commands


class ReglasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Aceptar reglas",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="reglas_aceptar"
    )
    async def aceptar_reglas(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild

        if guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )

        # Busca el rol "Verificado"
        rol = discord.utils.get(guild.roles, name="Verificado")

        if rol is None:
            return await interaction.response.send_message(
                "❌ No existe el rol `Verificado` en este servidor.",
                ephemeral=True
            )

        # Comprueba si ya tiene el rol
        if rol in interaction.user.roles:
            return await interaction.response.send_message(
                "✅ Ya aceptaste las reglas anteriormente.",
                ephemeral=True
            )

        try:
            await interaction.user.add_roles(
                rol,
                reason="Aceptó las reglas del servidor."
            )

            await interaction.response.send_message(
                "✅ **¡Reglas aceptadas!**\n"
                "Ahora tenés acceso al servidor.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo darte el rol `Verificado`.\n"
                "Asegurate de que mi rol esté por encima del rol `Verificado`.",
                ephemeral=True
            )


class Reglas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="reglas",
        description="Muestra las reglas del servidor."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reglas(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="📜 Reglas del servidor",
            description=(
                "Bienvenido/a al servidor.\n"
                "Antes de participar, leé y aceptá las siguientes reglas.\n\n"
                "Al presionar **Aceptar reglas**, confirmás que estás "
                "de acuerdo con las normas."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="1️⃣ Respeto",
            value=(
                "Tratamos a todos con respeto. "
                "No se permiten insultos, acoso, discriminación "
                "ni comportamientos tóxicos."
            ),
            inline=False
        )

        embed.add_field(
            name="2️⃣ Spam",
            value=(
                "No hagas spam, flood ni envíes mensajes repetitivos "
                "de manera excesiva."
            ),
            inline=False
        )

        embed.add_field(
            name="3️⃣ Publicidad",
            value=(
                "No está permitida la publicidad de otros servidores, "
                "bots o servicios sin autorización del staff."
            ),
            inline=False
        )

        embed.add_field(
            name="4️⃣ Contenido",
            value=(
                "No compartas contenido ilegal, malicioso o que pueda "
                "perjudicar a otros miembros."
            ),
            inline=False
        )

        embed.add_field(
            name="5️⃣ Uso de canales",
            value=(
                "Utilizá cada canal para el propósito correspondiente "
                "y respetá las indicaciones del staff."
            ),
            inline=False
        )

        embed.add_field(
            name="6️⃣ Staff",
            value=(
                "Respetá las decisiones del equipo de moderación. "
                "Si tenés un problema, contactá al staff."
            ),
            inline=False
        )

        embed.add_field(
            name="⚠️ Importante",
            value=(
                "El incumplimiento de las reglas puede resultar en "
                "advertencias, expulsiones o baneos según la gravedad."
            ),
            inline=False
        )

        embed.set_footer(
            text="Al aceptar las reglas recibirás el rol Verificado."
        )

        await interaction.response.send_message(
            embed=embed,
            view=ReglasView()
        )


async def setup(bot):
    await bot.add_cog(Reglas(bot))