import typing
from copy import copy
import time
import asyncio

import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.config import Config

RequestType = typing.Literal["discord_deleted_user", "owner", "user", "user_strict"]


class Execute(commands.Cog):
    """Combine multiple commands."""

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=623469945234523465,
            force_registration=True,
        )

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        return

    @checks.is_owner()
    @commands.command()
    async def execute(self, ctx, sequential: typing.Optional[bool] = False, *, commands):
        """Execute multiple commands at once. Split them using |."""
        commands = commands.split("|")
        if sequential:
            for command in commands:
                new_message = copy(ctx.message)
                new_message.content = ctx.prefix + command.strip()
                await self.bot.process_commands(new_message)
        else:
            todo = []
            for command in commands:
                new_message = copy(ctx.message)
                new_message.content = ctx.prefix + command.strip()
                todo.append(self.bot.process_commands(new_message))
            await asyncio.gather(*todo)
