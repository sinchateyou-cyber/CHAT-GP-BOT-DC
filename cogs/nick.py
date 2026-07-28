# =========================
# CAMBIAR APODO
# =========================
@commands.command(name="nick")
@commands.has_permissions(manage_nicknames=True)
async def nick(
    self,
    ctx,
    miembro: discord.Member,
    *,
    apodo: str
):
    try:
        apodo_anterior = miembro.display_name
        await miembro.edit(
            nick=apodo,
            reason=f"Apodo cambiado por {ctx.author}"
        )
        embed = discord.Embed(
            title="✏️ Apodo cambiado",
            description=(
                f"Se cambió el apodo de {miembro.mention}."
            )
        )
        embed.add_field(
            name="👤 Usuario",
            value=miembro.mention,
            inline=True
        )
        embed.add_field(
            name="📝 Apodo anterior",
            value=apodo_anterior,
            inline=True
        )
        embed.add_field(
            name="✨ Nuevo apodo",
            value=apodo,
            inline=True
        )
        await ctx.send(
            embed=embed
        )
    except discord.Forbidden:
        await ctx.send(
            "❌ No puedo cambiar el apodo de ese usuario. "
            "Asegurate de que mi rol esté por encima del suyo."
        )
# =========================
# ERROR DEL COMANDO
# =========================
@nick.error
async def nick_error(self, ctx, error):
    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        await ctx.send(
            "❌ Uso correcto: `!nick @usuario Nuevo Apodo`",
            delete_after=5
        )
    elif isinstance(
        error,
        commands.MissingPermissions
    ):
        await ctx.send(
            "❌ Necesitás el permiso "
            "**Gestionar apodos** para usar este comando.",
            delete_after=5
        )