import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os


DATA_FILE = "data/multimedia.json"


# ==========================
# ARCHIVO CONFIG
# ==========================

def load_data():

    if not os.path.exists("data"):
        os.makedirs("data")


    if not os.path.exists(DATA_FILE):

        with open(DATA_FILE, "w") as f:
            json.dump({}, f, indent=4)


    with open(DATA_FILE, "r") as f:
        return json.load(f)



def save_data(data):

    with open(DATA_FILE, "w") as f:
        json.dump(
            data,
            f,
            indent=4
        )



# ==========================
# COG
# ==========================

class Multimedia(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.check_status.start()



    def cog_unload(self):

        self.check_status.cancel()



    # ==========================
    # SISTEMA AUTOMATICO
    # ==========================

    @tasks.loop(seconds=60)
    async def check_status(self):

        data = load_data()


        for guild in self.bot.guilds:

            config = data.get(
                str(guild.id)
            )


            if not config:
                continue


            if not config.get(
                "enabled",
                False
            ):
                continue



            role = guild.get_role(
                int(config["role_id"])
            )


            if role is None:
                continue



            required_status = config.get(
                "status",
                ""
            )



            for member in guild.members:


                if member.bot:
                    continue


                has_status = False



                for activity in member.activities:


                    if isinstance(
                        activity,
                        discord.CustomActivity
                    ):

                        if activity.name:


                            if required_status.lower() in activity.name.lower():

                                has_status = True



                try:


                    if has_status:


                        if role not in member.roles:

                            await member.add_roles(
                                role,
                                reason="Estado multimedia detectado"
                            )



                    else:


                        if role in member.roles:

                            await member.remove_roles(
                                role,
                                reason="Estado multimedia eliminado"
                            )


                except:

                    pass




    # ==========================
    # GRUPO /CONFIG MULTIMEDIA
    # ==========================


    multimedia = app_commands.Group(
        name="multimedia",
        description="Configuración del sistema Multimedia"
    )



    @multimedia.command(
        name="activar",
        description="Activa el sistema multimedia"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def activar(
        self,
        interaction: discord.Interaction
    ):

        data = load_data()


        guild = str(
            interaction.guild.id
        )


        if guild not in data:

            data[guild] = {
                "enabled": True,
                "role_id": None,
                "status": ".gg/bandarg"
            }

        else:

            data[guild]["enabled"] = True



        save_data(data)



        await interaction.response.send_message(
            "🟣 Sistema Multimedia activado.",
            ephemeral=True
        )




    @multimedia.command(
        name="desactivar",
        description="Desactiva el sistema multimedia"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def desactivar(
        self,
        interaction: discord.Interaction
    ):

        data = load_data()

        guild = str(
            interaction.guild.id
        )


        if guild in data:

            data[guild]["enabled"] = False


        save_data(data)



        await interaction.response.send_message(
            "🔴 Sistema Multimedia desactivado.",
            ephemeral=True
        )




    @multimedia.command(
        name="rol",
        description="Configura el rol Multimedia"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def rol(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):


        data = load_data()


        guild = str(
            interaction.guild.id
        )


        if guild not in data:

            data[guild] = {
                "enabled": False,
                "role_id": rol.id,
                "status": ".gg/bandarg"
            }

        else:

            data[guild]["role_id"] = rol.id



        save_data(data)



        await interaction.response.send_message(
            f"✅ Rol configurado: {rol.mention}",
            ephemeral=True
        )




    @multimedia.command(
        name="estado",
        description="Texto que debe tener el estado"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def estado(
        self,
        interaction: discord.Interaction,
        texto: str
    ):


        data = load_data()


        guild = str(
            interaction.guild.id
        )


        if guild not in data:

            data[guild] = {
                "enabled": False,
                "role_id": None,
                "status": texto
            }

        else:

            data[guild]["status"] = texto



        save_data(data)



        await interaction.response.send_message(
            f"✅ Estado requerido cambiado a:\n`{texto}`",
            ephemeral=True
        )




    @multimedia.command(
        name="info",
        description="Muestra la configuración actual"
    )
    async def info(
        self,
        interaction: discord.Interaction
    ):

        data = load_data()


        config = data.get(
            str(interaction.guild.id)
        )


        if not config:

            return await interaction.response.send_message(
                "❌ No hay configuración.",
                ephemeral=True
            )



        embed = discord.Embed(
            title="🟣 Configuración Multimedia",
            color=0x8A2BE2
        )


        embed.add_field(
            name="Estado",
            value="Activado ✅" if config["enabled"] else "Desactivado ❌"
        )


        embed.add_field(
            name="Rol",
            value=f"<@&{config['role_id']}>" if config["role_id"] else "No configurado"
        )


        embed.add_field(
            name="Texto",
            value=config["status"]
        )


        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )




async def setup(bot):

    await bot.add_cog(
        Multimedia(bot)
    )