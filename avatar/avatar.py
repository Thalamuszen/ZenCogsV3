import discord

from datetime import datetime

from redbot.core import commands

BaseCog = getattr(commands, "Cog", object)

class Avatar(BaseCog):
    """Get user's avatar URL."""

    @commands.command()
    async def avatar(self, ctx, *, user: discord.Member=None):
        """Returns user avatar URL.

        User argument can be user mention, nickname, username, user ID.
        Default to yourself when no argument is supplied.
        """
        author = ctx.author

        if not user:
            user = author

        if user.is_avatar_animated():
            url = user.avatar_url_as(format="gif")
        if not user.is_avatar_animated():
            url = user.avatar_url_as(static_format="png")
            
        embed = discord.Embed(
            colour=await ctx.embed_colour(),
            description=f"Avatar [URL]({url})",
            timestamp=datetime.now(),
        )
        embed.set_image(url={url})
        embed.set_author(
            name=f"{user.name}'s Avatar",
        )            
        embed.set_footer(text="Avatary™")
        await ctx.send(embed=embed)            
