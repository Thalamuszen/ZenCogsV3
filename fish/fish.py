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

NAMES = {
    "\ud83d\udd27": "trash",
    "\ud83d\udd0b": "trash",
    "\ud83d\uded2": "trash",
    "\ud83d\udc20": "uncommon",
    "\ud83d\udc21": "uncommon",
    "\ud83d\udc1f": "common",
    "\ud83e\udd80": "common",
    "\ud83e\udd90": "common",
}
RARES = {
    "\ud83d\udc22": "turtle",
    "\ud83d\udc33": "blow whale",
    "\ud83d\udc0b": "whale",
    "\ud83d\udc0a": "crocodile",
    "\ud83d\udc27": "penguin",
    "\ud83d\udc19": "octopus",
    "\ud83e\udd88": "shark",      
    "\ud83e\udd91": "squid",  
    "\ud83d\udc2c": "dolphin",
}

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
            "trash": [
                "\ud83d\udd27",
                "\ud83d\udd0b",
                "\ud83d\uded2",
            ],
            "uncommon": [
                "\ud83d\udc20",
                "\ud83d\udc21", 
            ],
            "common": [
                "\ud83d\udc1f",
                "\ud83e\udd80",
                "\ud83e\udd90",
            ],
            "rarefish": [
                "\ud83d\udc22",
                "\ud83d\udc33",
                "\ud83d\udc0b",
                "\ud83d\udc0a",
                "\ud83d\udc27",
                "\ud83d\udc19",
                "\ud83e\udd88",
                "\ud83e\udd91",
                "\ud83d\udc2c",
            ],
        }

        default_guild = {"enabled": False, "cooldown": 30}

        default_user = {
            "turtle": 0,
            "blow_whale": 0,
            "whale": 0,
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


    @commands.command()
    @commands.guild_only()
    async def fish(self, ctx):
        """Go Fishing!"""

        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the lake is closed. Come back later!")
        
        author = ctx.message.author
        userdata = await self.config.user(ctx.author).all()
        last_time = datetime.datetime.strptime(str(userdata["last_fish"]), "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.datetime.now(datetime.timezone.utc)
        now = now.replace(tzinfo=None)
        seconds = int((now - last_time).total_seconds())
        cd = await self.config.guild(ctx.guild).cooldown()
        secs = cd - seconds
        if int((now - last_time).total_seconds()) < await self.config.guild(ctx.guild).cooldown():
            return await ctx.send(f":fishing_pole_and_fish: **| {author.name} you can fish again in {secs} seconds.**")
        await self.config.user(ctx.author).last_fish.set(str(now))            

        chance = uniform(1, 100)
        rarechance = 0.15
        uncommonchance = 10.15
        commonchance = 51

        if chance <= rarechance:
            rarefish = await self.config.rarefish()
            mn = len(rarefish)
            r = randint(0, mn - 1)
            fish = rarefish[r]
            await ctx.send(
                _(
                    ":fishing_pole_and_fish: **| {author.name} caught a rare fish!!! {fish} !**"
                    "*Type `!fish rarefish` to see your trophy room"
                ).format(
                    author=author,
                    fish=fish,
                )
            )
            try:
                item = RARES[fish]
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)
            except KeyError:
                item = RARES[fish]
                price = 2000
                author_quantity = 1           
                description = "Oooo shiny!"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": False,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )            
        elif rarechance < chance <= uncommonchance:
            uncommon = await self.config.uncommon()
            mn = len(uncommon)
            u = randint(0, mn - 1)
            fish = uncommon[u]
            await ctx.send(f":fishing_pole_and_fish: **| {author.name} caught an uncommon fish! {fish} !**")
            try:
                item = NAMES[fish]
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)
            except KeyError:
                item = NAMES[fish]
                price = 50
                author_quantity = 1 
                description = "Don't see these too often!"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": False,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )              
        elif uncommonchance < chance <= commonchance:
            common = await self.config.common()
            mn = len(common)
            c = randint(0, mn - 1)
            fish = common[c]
            await ctx.send(f":fishing_pole_and_fish: **| {author.name} caught a common fish {fish} !**")
            try:
                item = NAMES[fish]
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)
            except KeyError:
                item = NAMES[fish]
                price = 10
                author_quantity = 1 
                description = "Another one of these? Ok!"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": False,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )                
        elif chance > commonchance:
            trash = await self.config.trash()
            mn = len(trash)
            t = randint(0, mn - 1)
            fish = trash[t]
            await ctx.send(f":fishing_pole_and_fish: **| {author.name} caught a piece of trash.. {fish} !**")
            try:     
                item = NAMES[fish]
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)
            except KeyError:
                item = NAMES[fish]
                price = 5
                author_quantity = 1 
                description = "Ugh, trash"
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": author_quantity,
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": False,
                        "is_fish": True,
                        "redeemable": False,
                        "redeemed": False,
                        "description": description,             
                        "giftable": False,
                        "gifted": False,                         
                    },
                )
                
    @commands.command()
    @commands.guild_only()
    async def rarefish(self, ctx: commands.Context):
        """Shows which rare fish you have caught and how many"""
#        Need to do something within this cog regarding rare fish and how many you have caught.
#        Set default for each individual rare fish to 0 and then if it IS 0, don't show it, otherwise show emoji next to qty caught.
        userdata = await self.config.user(ctx.author).all()
        msg = f"{ctx.author.name}'s Rare Fish Trophy Wall"
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
        await ctx.send(msg, embed=em)  

    @commands.command()
    @commands.guild_only()
    async def net(self, ctx: commands.Context):
        inventory = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw()
        lst = []
        for i in inventory:
            try:
                info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(i)
                is_fish = info.get("is_fish")
                if is_fish:
                    quantity = info.get("quantity")
                    cat = "Fish"
                    table = [cat, i, quantity]
                    lst.append(table)
            except KeyError:
                pass
        if lst == []:
            output = "Nothing to see here, go fishing with `!fish`"
        else:
            headers = ("", "Type", "Item", "Qty") 
            output = box(tabulate(lst, headers=headers), lang="md")
        embed = discord.Embed(
            colour=await ctx.embed_colour(),
            description=f"{output}",
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/768197304158257234/777119363115384862/Net.png")
        embed.set_author(
            name=f"{ctx.author.display_name}'s fishing net", icon_url=ctx.author.avatar_url,
        )            
        embed.set_footer(text="Inventory™")
        await ctx.send(embed=embed)    
