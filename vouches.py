"""
vouches.py — /vouch, /vouches, /deletevouch
"""

import discord
from discord import app_commands
from discord.ext import commands
import datetime

import database as db
import utils

STAR_MAP = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}


class Vouches(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="vouch", description="Leave a vouch for the service.")
    @app_commands.describe(
        stars="Rating from 1–5",
        content="Your review (max 500 chars)",
    )
    @app_commands.choices(stars=[app_commands.Choice(name=str(i), value=i) for i in range(1, 6)])
    async def vouch(self, interaction: discord.Interaction, stars: int, content: str):
        content = content[:500]
        vouch_id = db.add_vouch(str(interaction.user.id), content, stars)
        embed = discord.Embed(
            color=0x57F287,
            title="✅ Vouch Submitted",
            description=f"{STAR_MAP.get(stars, '⭐')} **{content}**",
        )
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Vouch #{vouch_id} • Generator")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embeds=[embed])

    @app_commands.command(name="vouches", description="Show recent vouches.")
    @app_commands.describe(limit="Number of vouches to display (1–20)")
    async def vouches(self, interaction: discord.Interaction, limit: int = 10):
        limit = max(1, min(limit, 20))
        vouches = db.get_vouches(limit)

        embed = discord.Embed(
            color=0x5865F2,
            title=f"⭐ Recent Vouches ({len(vouches)})",
        ).set_footer(text="Generator")
        embed.timestamp = discord.utils.utcnow()

        if not vouches:
            embed.description = "No vouches yet. Be the first!"
        else:
            lines = []
            for v in vouches:
                stars = STAR_MAP.get(v.get("stars", 5), "⭐")
                user_id = v.get("user_id", "?")
                content = v.get("content", "")[:80]
                lines.append(f"{stars} <@{user_id}> — {content}")
            embed.description = "\n".join(lines)

        await interaction.response.send_message(embeds=[embed])

    @app_commands.command(name="deletevouch", description="[Owner] Delete a vouch by ID.")
    @app_commands.describe(vouch_id="ID of the vouch to delete")
    async def deletevouch(self, interaction: discord.Interaction, vouch_id: int):
        if not await utils.owner_only(interaction):
            return
        removed = db.delete_vouch(vouch_id)
        if removed:
            embed = discord.Embed(color=0x57F287, title="✅ Vouch Deleted",
                                  description=f"Vouch #{vouch_id} has been removed.")
        else:
            embed = discord.Embed(color=0xED4245, title="❌ Not Found",
                                  description=f"No vouch with ID **{vouch_id}** found.")
        embed.set_footer(text="Generator")
        await interaction.response.send_message(embeds=[embed], ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Vouches(bot))
