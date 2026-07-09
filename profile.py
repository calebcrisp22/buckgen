"""
profile.py — /profile /invites /inviteleaderboard
"""

import time
import discord
from discord import app_commands
from discord.ext import commands

import database as db
import utils

TIER_EMOJI = {"none": "⬜", "free": "🟩", "free+": "🟦", "premium": "🟨"}


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your profile (or another user's).")
    @app_commands.describe(user="User to look up (defaults to yourself)")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        u = db.get_user(str(target.id))

        tier = u.get("subscription", "none")
        expires = u.get("sub_expires", 0)
        now = int(time.time())
        is_active = tier != "none" and (expires == 0 or expires > now)
        expiry_str = utils.format_expires(expires)

        invites = db.get_inviter_joins(str(target.id))

        embed = discord.Embed(
            color=0x5865F2,
            title=f"{TIER_EMOJI.get(tier, '⬜')} {target.display_name}'s Profile",
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Subscription",
                        value=f"{tier.capitalize()} ({'Active' if is_active else 'Inactive'})", inline=True)
        embed.add_field(name="Expires",    value=expiry_str, inline=True)
        embed.add_field(name="Tokens",     value=str(u.get("tokens", 0)), inline=True)
        embed.add_field(name="Messages",   value=str(u.get("messages", 0)), inline=True)
        embed.add_field(name="Invites",    value=str(invites), inline=True)
        embed.set_footer(text="Generator")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embeds=[embed], ephemeral=True)

    @app_commands.command(name="invites", description="Check how many members you've invited.")
    @app_commands.describe(user="User to check (defaults to yourself)")
    async def invites(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        count = db.get_inviter_joins(str(target.id))
        embed = discord.Embed(
            color=0x5865F2,
            title=f"📨 Invites — {target.display_name}",
            description=f"{target.mention} has invited **{count}** member(s).",
        ).set_footer(text="Generator")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embeds=[embed])

    @app_commands.command(name="inviteleaderboard", description="Show the top inviters.")
    async def inviteleaderboard(self, interaction: discord.Interaction):
        lb = db.get_inviter_leaderboard()
        embed = discord.Embed(
            color=0x5865F2,
            title="🏆 Invite Leaderboard",
        ).set_footer(text="Generator")
        embed.timestamp = discord.utils.utcnow()

        if not lb:
            embed.description = "No invite data yet."
        else:
            medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 10
            lines = []
            for i, entry in enumerate(lb):
                lines.append(f"{medals[i]} <@{entry['inviter_id']}> — **{entry['count']}** invite(s)")
            embed.description = "\n".join(lines)

        await interaction.response.send_message(embeds=[embed])


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
