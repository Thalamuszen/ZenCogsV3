from .execute import execute

__red_end_user_data_statement__ = "This cog does not store any End User Data. Author IDS are stored when creating an embed, and this cannot be deleted to keep authors accountable for the embeds they store."

def setup(bot):
    n = execute(bot)
    bot.add_cog(n)
