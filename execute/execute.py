import discord
import asyncio
import typing
import json
import io

from redbot.core import commands, checks, Config
from redbot.core.utils import menus

@checks.is_owner()
@commands.command()
async def execute(self, ctx, sequential: typing.Optional[bool] = False, *, commands):
    """Execute multiple commands at once. Split them using |"""
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
