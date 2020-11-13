import asyncio
import datetime
import discord
import logging

from random import uniform, randint
from discord.utils import get

from redbot.core import commands, checks, Config, bank
from redbot.core.utils.chat_formatting import box, humanize_list, pagify

from redbot.core.bot import Red


log = logging.getLogger("red.zen.fish")


class Fish(commands.Cog):
    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    __author__ = "ThalamusZen"
    __version__ = "0.6.9"    

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, 4119811374891, force_registration=True)

        default_global = {
            trash = [
                "wrench": "\ud83d\udd27",
                "battery": "\ud83d\udd0b",
                "shopping_cart": "\ud83d\uded2",
            ],
            uncommon = [
                "tropical_fish": "\ud83d\udc20",
                "blowfish": "\ud83d\udc21", 
            ],
            common = [
                "fish": "\ud83d\udc1f",
                "crab": "\ud83e\udd80",
                "shrimp": "\ud83e\udd90",
            ],
            rarefish = [
                "turtle": "\ud83d\udc22",
                "whale": "\ud83d\udc33",
                "whale2": "\ud83d\udc0b",
                "crocodile": "\ud83d\udc0a",
                "penguin": "\ud83d\udc27",
                "octopus": "\ud83d\udc19",
                "shark": "\ud83e\udd88",
                "squid": "\ud83e\udd91",
                "dolphin": "\ud83d\udc2c",
            ],
        }

        default_guild = {"enabled": False, "cooldown": 30}

        default_user = {
            "turtle": 0,
            "whale": 0,
            "whale2": 0,
            "crocodile": 0,
            "penguin": 0,
            "octopus": 0,
            "shark": 0,
            "squid": 0,
            "dolphin": 0,            
            "last_fish": "2020-01-01 00:00:00.000001",
        }

        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        self.config.register_user(**default_user)

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def fishy(self, ctx):
        """Admin fishing settings."""
        pass

    @fishy.command(name="toggle")
    async def store_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle fishing for the current server.
        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).enabled())
        )
        await self.config.guild(ctx.guild).enabled.set(target_state)
        if target_state:
            await ctx.send("Fishing is now enabled.")
        else:
            await ctx.send("Fishing is now disabled.")


    @commands.group()
    @commands.guild_only()
    async def fish(self, ctx):
        """Base fishing command."""

        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the lake is closed. Come back later!")
        
        author = ctx.message.author

        last_time = datetime.datetime.strptime(str(userdata["last_fish"]), "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.datetime.now(datetime.timezone.utc)
        now = now.replace(tzinfo=None)
        secs = int((now - last_time).total_seconds())
        if int((now - last_time).total_seconds()) < await self.config.guild(message.guild).cooldown():
            return await ctx.send(f":fishing_pole_and_fish: **| {author.name} you can fish again in {secs} seconds.**")
        await self.config.user(message.author).last_fish.set(str(now))            

        chance = uniform(1, 100)
        rarechance = 0.15
        uncommonchance = 10.15
        commonchance = 51

        if chance <= rarechance:
            rarefish = await self.config.rarefish()
            mn = len(rarefish)
            r = randint(0, mn)
            fish = rarefish[r]
            await ctx.send(":fishing_pole_and_fish: **| {author.name} caught: {fish} !**")
            try:
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(fish)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(fish, "quantity", value=author_quantity)
            except KeyError:
                price = 2000
                description = "Oooo shiny!"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    fish,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": True,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )            
        elif chance > rarechance <= uncommonchance:
            uncommon = await self.config.uncommon()
            mn = len(uncommon)
            u = randint(0, mn)
            fish = uncommon[r]
            await ctx.send(":fishing_pole_and_fish: **| {author.name} caught: {fish} !**")
            try:
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(fish)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(fish, "quantity", value=author_quantity)
            except KeyError:
                price = 50
                description = "Don't see these too often!"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    fish,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": True,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )              
        elif chance > uncommonchance <= commonchance:
            common = await self.config.common()
            mn = len(common)
            c = randint(0, mn)
            fish = common[r]
            await ctx.send(":fishing_pole_and_fish: **| {author.name} caught: {fish} !**")
            try:
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(fish)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(fish, "quantity", value=author_quantity)
            except KeyError:
                price = 10
                description = "Another one of these? Ok!"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    fish,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": True,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )                
        elif chance > commonchance
            trash = await self.config.trash()
            mn = len(trash)
            t = randint(0, mn)
            fish = trash[r]
            await ctx.send(":fishing_pole_and_fish: **| {author.name} caught: {fish} !**")
            try:              
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(fish)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(fish, "quantity", value=author_quantity)
            except KeyError:
                price = 5
                description = "Ugh, trash"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    fish,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": True,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )              

    @fish.command(name="rarefish")
    async def fish_rarefish(self, ctx: commands.Context):
        """Shows which rare fish you have caught and how many"""
        Need to do something within this cog regarding rare fish and how many you have caught.
        Set default for each individual rare fish to 0 and then if it IS 0, don't show it, otherwise show emoji next to qty caught.

        userdata = await self.config.user(ctx.author).all()
        msg = f"{ctx.author.name}'s Rare Fish Troph Wall"
        em = discord.Embed(color=await ctx.embed_color())
        em.description = f"{userdata['candies']} \N{CANDY}"
        if userdata["chocolate"]:
            em.description += f"\n{userdata['chocolate']} \N{CHOCOLATE BAR}"
        if userdata["lollipops"]:
            em.description += f"\n{userdata['lollipops']} \N{LOLLIPOP}"
        if userdata["stars"]:
            em.description += f"\n{userdata['stars']} \N{WHITE MEDIUM STAR}"
        if sickness in range(41, 56):
            em.description += f"\n\n**Sickness is over 40/100**\n*You don't feel so good...*"
        elif sickness in range(56, 71):
            em.description += f"\n\n**Sickness is over 55/100**\n*You don't feel so good...*"
        elif sickness in range(71, 86):
            em.description += f"\n\n**Sickness is over 70/100**\n*You really don't feel so good...*"
        elif sickness in range(86, 101):
            em.description += f"\n\n**Sickness is over 85/100**\n*The thought of more sugar makes you feel awful...*"
        elif sickness > 100:
            em.description += f"\n\n**Sickness is over 100/100**\n*Better wait a while for more candy...*"
        await ctx.send(msg, embed=em)

    @fish.command(name="sell")
    async def fish_sell(self, ctx: commands.Context, group: str = ""):
        """Sell your trash/uncommon/common/rare fish"""

        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the fishing shop is closed. Come back later!")