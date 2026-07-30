@app_commands.command(
    name="play",
    description="Reproduce una canción."
)
@app_commands.describe(
    busqueda="Nombre o URL de la canción."
)
async def play(
    self,
    interaction: discord.Interaction,
    busqueda: str
):
    # Acá va el código que reproduce la música
    pass