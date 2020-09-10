import discord
import asyncio
import typing
import tracemalloc

from redbot.core import commands, checks

from redbot.core.bot import Red

class Execute(commands.Cog):
    """
    Combine multiple commands.
    """
    
    def __init__(self, bot: Red):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
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
