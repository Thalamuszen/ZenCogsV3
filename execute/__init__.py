from .execute import Execute

def setup(bot):
    cog = Execute(bot)
    bot.add_cog(cog)
