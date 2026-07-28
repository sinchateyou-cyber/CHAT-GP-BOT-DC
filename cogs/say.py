# =========================
# SAY
# =========================
@commands.command(name="say")
@commands.has_permissions(administrador=True)
async def say(self, ctx, *, mensaje: str):
    # Borra el mensaje del usuario
    await ctx.message.delete()
    # Envía el mensaje
    await ctx.send(mensaje)
# =========================
# ERROR SAY
# =========================
@say.error
async def say_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"❌ {ctx.author.mention}, escribí un mensaje.\n"
            f"Ejemplo: `!say Hola a todos`",
            delete_after=5
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(
            f"❌ {ctx.author.mention}, no tenés permisos para usar este comando.",
            delete_after=5
        )