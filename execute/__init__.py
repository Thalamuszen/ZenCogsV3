import json
from pathlib import Path

from redbot.core.bot import Red

from .execute import Execute

async def setup(bot: Red) -> None:
    bot.add_cog(Execute(bot))
