import discord
from discord import app_commands
from discord.ext import commands


class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban", description="Desbanea a un usuario por su ID.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            usuario = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(usuario)

            await interaction.response.send_message(
                f"✅ **{usuario}** fue desbaneado."
            )

        except ValueError:
            await interaction.response.send_message(
                "❌ La ID ingresada no es válida.",
                ephemeral=True
            )

        except discord.NotFound:
            await interaction.response.send_message(
                "❌ Ese usuario no está baneado.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para desbanear.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Unban(bot))