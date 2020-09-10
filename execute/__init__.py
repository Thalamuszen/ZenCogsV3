from .execute import execute


def setup(bot):
    n = execute()
    bot.add_cog(n)