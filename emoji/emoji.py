import re

from redbot.core import checks, Config, commands

PATTERN = re.compile(r"w+h*[aou]+t+[?!]*", re.IGNORECASE)


class Emoji(commands.Cog):

    """Enlarges someone another users Emoji"""

    default_global_settings = {"channels_ignored": [], "guilds_ignored": []}

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier=527690525)
        self.conf.register_global(**self.default_global_settings)

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.group(name="emojiignore", pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_guild=True)
    async def emojiignore(self, ctx):
        """Change Emoji cog ignore settings."""
        pass

    @commands.command()
    async def emoji(self, message):
        if message.guild is None:
            return
        if message.author.bot:
            return

        if PATTERN.fullmatch(content[0]):
            async for before in message.channel.history(limit=5, before=message):
                author = before.author
                name = author.display_name
                if (
                    not author.bot
                    and not author == message.author
                ):
                    emoji = "\N{CHEERING MEGAPHONE}"
                    msg = f"{name} said, **{emoji}   {content}**"
                    await message.channel.send(msg)
                    break
