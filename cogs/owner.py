# =========================
# OWNER
# =========================
@commands.command(name="owner")
async def owner(self, ctx):
    embed = discord.Embed(
        title="👑 Dueño del Bot",
        description=(
            "Este bot fue creado y desarrollado por su propietario."
        )
    )
    embed.add_field(
        name="👤 Owner",
        value="Valentin",
        inline=False
    )
    embed.add_field(
        name="🤖 Bot",
        value=self.bot.user.mention,
        inline=False
    )
    embed.set_thumbnail(
        url=self.bot.user.display_avatar.url
    )
    embed.set_footer(
        text="Gracias por usar el bot."
    )
    await ctx.send(
        embed=embed
    )