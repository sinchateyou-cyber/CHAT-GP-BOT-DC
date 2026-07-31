import discord
from discord.ext import commands, tasks
class RichPresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.presence_index = 0
        # Inicia la actualización automática
        self.update_presence.start()
    def cog_unload(self):
        self.update_presence.cancel()
    # ============================================================
    # PRESENCIA AUTOMÁTICA
    # ============================================================
    @tasks.loop(seconds=30)
    async def update_presence(self):
        # Cantidad de servidores
        servidores = len(self.bot.guilds)
        # Cantidad total de usuarios
        usuarios = sum(
            guild.member_count or 0
            for guild in self.bot.guilds
        )
        # Cantidad de comandos slash
        comandos = len(self.bot.tree.get_commands())
        # Diferentes actividades
        actividades = [
            discord.Game(
                name=f"Optik | {servidores} servidores"
            ),
            discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{usuarios:,} usuarios"
            ),
            discord.Activity(
                type=discord.ActivityType.listening,
                name=f"/help | {comandos} comandos"
            ),
            discord.Activity(
                type=discord.ActivityType.watching,
                name="tu servidor"
            )
        ]
        # Selecciona la actividad actual
        actividad = actividades[
            self.presence_index
        ]
        # Cambia la presencia
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=actividad
        )
        # Pasa a la siguiente actividad
        self.presence_index += 1
        if self.presence_index >= len(actividades):
            self.presence_index = 0
    # ============================================================
    # ESPERAR A QUE EL BOT ESTÉ LISTO
    # ============================================================
    @update_presence.before_loop
    async def before_update_presence(self):
        await self.bot.wait_until_ready()
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        RichPresence(bot)
    )