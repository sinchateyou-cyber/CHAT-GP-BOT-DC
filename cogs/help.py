import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Muestra todos los comandos disponibles."
    )
    async def help(
        self,
        interaction: discord.Interaction
    ):
        try:

            embed = discord.Embed(
                title="📚 Centro de Ayuda",
                description=(
                    "Estos son los comandos disponibles "
                    "en el servidor."
                ),
                color=discord.Color.blurple()
            )

            embed.add_field(
                name="🛡️ Moderación",
                value=(
                    "`/ban` — Banea a un usuario.\n"
                    "`/kick` — Expulsa a un usuario.\n"
                    "`/timeout` — Silencia a un usuario.\n"
                    "`/untimeout` — Quita el timeout.\n"
                    "`/clear` — Borra mensajes."
                ),
                inline=False
            )

            embed.add_field(
                name="🔐 Seguridad",
                value=(
                    "`/verificacion` — Envía el panel de verificación.\n"
                    "`/server-setup` — Configura el servidor."
                ),
                inline=False
            )

            embed.add_field(
                name="👤 Usuarios",
                value=(
                    "`/avatar` — Muestra el avatar.\n"
                    "`/userinfo` — Muestra información de un usuario.\n"
                    "`/afk` — Activa el modo AFK."
                ),
                inline=False
            )

            embed.add_field(
                name="🎭 Roles",
                value=(
                    "`/roles` — Abre el panel de roles.\n"
                    "`/addrole` — Agrega un rol.\n"
                    "`/createrole` — Crea un rol."
                ),
                inline=False
            )

            embed.add_field(
                name="⭐ Sistema XP",
                value=(
                    "`/level` — Mira tu nivel.\n"
                    "`/rank` — Mira tu ranking.\n"
                    "`/addxp` — Agrega XP.\n"
                    "`/addlevel` — Agrega niveles."
                ),
                inline=False
            )

            embed.add_field(
                name="🎵 Música",
                value=(
                    "`/play` — Reproduce música.\n"
                    "`/stop` — Detiene la música.\n"
                    "`/leave` — Hace salir al bot."
                ),
                inline=False
            )

            embed.set_footer(
                text=f"Solicitado por {interaction.user}"
            )

            # RESPUESTA INMEDIATA
            await interaction.response.send_message(
                embed=embed
            )

        except Exception as error:

            print(
                f"❌ Error en /help: "
                f"{type(error).__name__}: {error}"
            )

            try:

                if interaction.response.is_done():

                    await interaction.followup.send(
                        "❌ Ocurrió un error al mostrar la ayuda.",
                        ephemeral=True
                    )

                else:

                    await interaction.response.send_message(
                        "❌ Ocurrió un error al mostrar la ayuda.",
                        ephemeral=True
                    )

            except Exception as send_error:

                print(
                    f"❌ No se pudo responder al error: "
                    f"{send_error}"
                )


async def setup(bot):

    await bot.add_cog(
        Help(bot)
    )