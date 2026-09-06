import json
from pathlib import Path
import discord
from discord.ext import commands
from discord import app_commands
DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "marriages.json"
class Marry(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        DATA_FOLDER.mkdir(parents=True, exist_ok=True)
        if not DATA_FILE.exists():
            DATA_FILE.write_text("{}", encoding="utf-8")
        self.marriages = self.load_data()
    # =========================================================
    # DATOS
    # =========================================================
    def load_data(self):
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    def save_data(self):
        DATA_FILE.write_text(
            json.dumps(self.marriages, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )
    def get_partner(self, user_id: int):
        user_id = str(user_id)
        for person, partner in self.marriages.items():
            if person == user_id:
                return int(partner)
            if partner == user_id:
                return int(person)
        return None
    # =========================================================
    # /MARRY
    # =========================================================
    @app_commands.command(
        name="marry",
        description="💍 Proponé matrimonio a otro usuario."
    )
    @app_commands.describe(
        usuario="La persona a la que querés proponerle matrimonio."
    )
    async def marry(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        autor = interaction.user
        if usuario.bot:
            await interaction.response.send_message(
                "🤨 No podés casarte con un bot.",
                ephemeral=True
            )
            return
        if usuario.id == autor.id:
            await interaction.response.send_message(
                "💀 No podés casarte con vos mismo.",
                ephemeral=True
            )
            return
        if self.get_partner(autor.id):
            await interaction.response.send_message(
                "💍 Ya estás casado/a.",
                ephemeral=True
            )
            return
        if self.get_partner(usuario.id):
            await interaction.response.send_message(
                f"💍 {usuario.mention} ya está casado/a.",
                ephemeral=True
            )
            return
        embed = discord.Embed(
            title="💍 ¡Propuesta de matrimonio!",
            description=(
                f"{autor.mention} quiere casarse con {usuario.mention} 💕\n\n"
                f"**{usuario.display_name}**, ¿aceptás?"
            ),
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_footer(
            text="La propuesta expira en 60 segundos."
        )
        view = MarriageView(
            cog=self,
            proposer=autor,
            target=usuario
        )
        await interaction.response.send_message(
            content=usuario.mention,
            embed=embed,
            view=view
        )
        view.message = await interaction.original_response()
    # =========================================================
    # /DIVORCE
    # =========================================================
    @app_commands.command(
        name="divorce",
        description="💔 Divorciate de tu pareja."
    )
    async def divorce(self, interaction: discord.Interaction):
        usuario = interaction.user
        partner_id = self.get_partner(usuario.id)
        if not partner_id:
            await interaction.response.send_message(
                "💔 No estás casado/a.",
                ephemeral=True
            )
            return
        self.marriages.pop(str(usuario.id), None)
        self.marriages.pop(str(partner_id), None)
        self.save_data()
        try:
            partner = await self.bot.fetch_user(partner_id)
            partner_name = partner.mention
        except discord.HTTPException:
            partner_name = f"<@{partner_id}>"
        embed = discord.Embed(
            title="💔 Divorcio",
            description=(
                f"{usuario.mention} y {partner_name} "
                "ya no están casados. 💔"
            ),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    # =========================================================
    # /MARRIAGE
    # =========================================================
    @app_commands.command(
        name="marriage",
        description="💍 Mirá con quién estás casado/a."
    )
    @app_commands.describe(
        usuario="Usuario que querés consultar."
    )
    async def marriage(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):
        usuario = usuario or interaction.user
        partner_id = self.get_partner(usuario.id)
        if not partner_id:
            await interaction.response.send_message(
                f"💔 {usuario.mention} no está casado/a.",
                ephemeral=True
            )
            return
        try:
            partner = await self.bot.fetch_user(partner_id)
        except discord.HTTPException:
            partner = None
        partner_mention = (
            partner.mention
            if partner
            else f"<@{partner_id}>"
        )
        embed = discord.Embed(
            title="💍 Matrimonio",
            description=(
                f"**{usuario.display_name}** está casado/a con "
                f"{partner_mention} 💕"
            ),
            color=discord.Color.from_rgb(255, 105, 180)
        )
        await interaction.response.send_message(embed=embed)
    # =========================================================
    # /COUPLES
    # =========================================================
    @app_commands.command(
        name="couples",
        description="💞 Ver las parejas del servidor."
    )
    async def couples(self, interaction: discord.Interaction):
        parejas = []
        for user_id, partner_id in self.marriages.items():
            # Evitar mostrar cada pareja dos veces
            if int(user_id) > int(partner_id):
                continue
            user = interaction.guild.get_member(int(user_id))
            partner = interaction.guild.get_member(int(partner_id))
            if user and partner:
                parejas.append(
                    f"💍 {user.mention} ❤️ {partner.mention}"
                )
        if not parejas:
            await interaction.response.send_message(
                "💔 Todavía no hay parejas casadas en este servidor."
            )
            return
        embed = discord.Embed(
            title="💞 Parejas del servidor",
            description="\n".join(parejas[:20]),
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.set_footer(
            text=f"{len(parejas)} pareja(s)"
        )
        await interaction.response.send_message(embed=embed)
# =============================================================
# VIEW DE PROPUESTA
# =============================================================
class MarriageView(discord.ui.View):
    def __init__(
        self,
        cog: Marry,
        proposer: discord.Member,
        target: discord.Member
    ):
        super().__init__(timeout=60)
        self.cog = cog
        self.proposer = proposer
        self.target = target
        self.message = None
    async def interaction_check(
        self,
        interaction: discord.Interaction
    ) -> bool:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                "💍 Esta propuesta no es para vos.",
                ephemeral=True
            )
            return False
        return True
    # =========================================================
    # ACEPTAR
    # =========================================================
    @discord.ui.button(
        label="Aceptar",
        emoji="💍",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if self.cog.get_partner(self.proposer.id):
            await interaction.response.send_message(
                "💔 La propuesta ya no es válida.",
                ephemeral=True
            )
            self.stop()
            return
        if self.cog.get_partner(self.target.id):
            await interaction.response.send_message(
                "💔 Ya estás casado/a.",
                ephemeral=True
            )
            self.stop()
            return
        self.cog.marriages[str(self.proposer.id)] = str(
            self.target.id
        )
        self.cog.save_data()
        embed = discord.Embed(
            title="💍 ¡SE CASARON!",
            description=(
                f"🎉 {self.proposer.mention} y "
                f"{self.target.mention} ahora están casados. 💕\n\n"
                "Que sean felices para siempre... o hasta "
                "que usen `/divorce` 😂"
            ),
            color=discord.Color.from_rgb(255, 105, 180)
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=self
        )
        self.stop()
    # =========================================================
    # RECHAZAR
    # =========================================================
    @discord.ui.button(
        label="Rechazar",
        emoji="💔",
        style=discord.ButtonStyle.danger
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="💔 Propuesta rechazada",
            description=(
                f"{self.target.mention} rechazó la propuesta de "
                f"{self.proposer.mention}. 😭"
            ),
            color=discord.Color.red()
        )
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=self
        )
        self.stop()
    async def on_timeout(self):
        if self.message:
            embed = discord.Embed(
                title="⌛ Propuesta expirada",
                description=(
                    f"La propuesta de {self.proposer.mention} "
                    f"a {self.target.mention} expiró. 💔"
                ),
                color=discord.Color.dark_grey()
            )
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(
                    embed=embed,
                    view=self
                )
            except discord.HTTPException:
                pass
async def setup(bot: commands.Bot):
    await bot.add_cog(Marry(bot))