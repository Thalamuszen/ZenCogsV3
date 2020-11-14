import asyncio
import datetime
import discord
import logging

from random import uniform, randint
from discord.utils import get
from datetime import datetime, timezone
from tabulate import tabulate
from operator import itemgetter

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
    
    @fishy.command(name="rarereset")
    async def rare_reset(self, ctx: commands.Context, user: discord.Member):
        """Reset someones Trophy room"""
        userdata = await self.config.user(ctx.author).all()        
        if userdata["turtle"]:
            number = userdata['turtle']
            await self.config.user(user).turtle.set(userdata["turtle"] - number)  
        if userdata["blow_whale"]:    
            number = userdata['blow_whale']            
            await self.config.user(user).blow_whale.set(userdata["blow_whale"] - number)
        if userdata["whale"]:     
            number = userdata['whale']            
            await self.config.user(user).whale.set(userdata["whale"] - number)
        if userdata["crocodile"]:  
            number = userdata['crocodile']            
            await self.config.user(user).crocodile.set(userdata["crocodile"] - number)
        if userdata["penguin"]:
            number = userdata['penguin']            
            await self.config.user(user).penguin.set(userdata["penguin"] - number)        
        if userdata["octopus"]:       
            number = userdata['octopus']           
            await self.config.user(user).octopus.set(userdata["octopus"] - number)           
        if userdata["shark"]:           
            number = userdata['shark']            
            await self.config.user(user).shark.set(userdata["shark"] - number)          
        if userdata["squid"]:     
            number = userdata['squid']            
            await self.config.user(user).squid.set(userdata["squid"] - number)        
        if userdata["dolphin"]:
            number = userdata['dolphin']            
            await self.config.user(user).dolphin.set(userdata["dolphin"] - number)          

    @commands.command()
    @commands.guild_only()
    async def fish(self, ctx):
        """Go Fishing!"""

        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the lake is closed. Come back later!")
        
        author = ctx.message.author
        userdata = await self.config.user(ctx.author).all()
        last_time = datetime.strptime(str(userdata["last_fish"]), "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.now(timezone.utc)
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
                (
                    ":fishing_pole_and_fish: **| {author.name} caught a rare fish!!! {fish} !**\n"
                    "Type `!rarefish` to see your trophy room"
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
                if item is "turtle":
                    await self.config.user(ctx.author).turtle.set(userdata["turtle"] + 1)
                elif item is "blow_whale":
                    await self.config.user(ctx.author).blow_whale.set(userdata["blow_whale"] + 1)
                elif item is "whale":
                    await self.config.user(ctx.author).whale.set(userdata["whale"] + 1)  
                elif item is "crocodile":
                    await self.config.user(ctx.author).crocodile.set(userdata["crocodile"] + 1)
                elif item is "penguin":
                    await self.config.user(ctx.author).penguin.set(userdata["penguin"] + 1)
                elif item is "octopus":
                    await self.config.user(ctx.author).octopus.set(userdata["octopus"] + 1)   
                elif item is "shark":
                    await self.config.user(ctx.author).shark.set(userdata["shark"] + 1)  
                elif item is "squid":
                    await self.config.user(ctx.author).squid.set(userdata["squid"] + 1) 
                elif item is "dolphin":
                    await self.config.user(ctx.author).dolphin.set(userdata["dolphin"] + 1)                       
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
                if item is "turtle":
                    await self.config.user(ctx.author).turtle.set(userdata["turtle"] + 1)
                elif item is "blow_whale":
                    await self.config.user(ctx.author).blow_whale.set(userdata["blow_whale"] + 1)   
                elif item is "whale":
                    await self.config.user(ctx.author).whale.set(userdata["whale"] + 1)  
                elif item is "crocodile":
                    await self.config.user(ctx.author).crocodile.set(userdata["crocodile"] + 1)
                elif item is "penguin":
                    await self.config.user(ctx.author).penguin.set(userdata["penguin"] + 1)
                elif item is "octopus":
                    await self.config.user(ctx.author).octopus.set(userdata["octopus"] + 1)   
                elif item is "shark":
                    await self.config.user(ctx.author).shark.set(userdata["shark"] + 1)  
                elif item is "squid":
                    await self.config.user(ctx.author).squid.set(userdata["squid"] + 1) 
                elif item is "dolphin":
                    await self.config.user(ctx.author).dolphin.set(userdata["dolphin"] + 1)                     
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
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the lake is closed. Come back later!")
        userdata = await self.config.user(ctx.author).all()
        msg = f"{ctx.author.name}'s Rare Fish Trophy Wall"
        em = discord.Embed(color=await ctx.embed_color())
        em.description = f"Here you can see all of the rare fish you have and how many!\nGotta catch them all"
        if userdata["turtle"]:
            number = userdata['turtle']
            em.description += f"\n{number} {userdata['turtle']} \N{TURTLE}"
        if userdata["blow_whale"]:
            number = userdata['blow_whale']
            em.description += f"\n{number} {userdata['blow_whale']} \N{TURTLE}"
        if userdata["whale"]:
            number = userdata['whale']
            em.description += f"\n{number} {userdata['whale']} \N{TURTLE}"
        if userdata["crocodile"]:
            number = userdata['crocodile']
            em.description += f"\n{number} {userdata['crocodile']} \N{TURTLE}"            
        if userdata["penguin"]:
            number = userdata['penguin']
            em.description += f"\n{number} {userdata['penguin']} \N{TURTLE}"            
        if userdata["octopus"]:
            number = userdata['octopus']
            em.description += f"\n{number} {userdata['octopus']} \N{TURTLE}"   
        if userdata["shark"]:
            number = userdata['shark']
            em.description += f"\n{number} {userdata['shark']} \N{TURTLE}"  
        if userdata["squid"]:
            number = userdata['squid']
            em.description += f"\n{number} {userdata['squid']} \N{TURTLE}"              
        if userdata["dolphin"]:
            number = userdata['dolphin']
            em.description += f"\n{number} {userdata['dolphin']} \N{TURTLE}"              
        await ctx.send(msg, embed=em)  

    @commands.command()
    @commands.guild_only()
    async def net(self, ctx: commands.Context):
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the lake is closed. Come back later!")        
        inventory = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw()
        lst = []
        for i in inventory:
            try:
                info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(i)
                is_fish = info.get("is_fish")
                if is_fish:
                    quantity = info.get("quantity")
                    price = info.get("price")
                    table = [i, price, quantity]
                    lst.append(table)
                    sorted_lst = sorted(lst, key=itemgetter(1), reverse=True)
            except KeyError:
                pass
        if lst == []:
            output = "Nothing to see here, go fishing with `!fish`"
        else:
            headers = ("Type", "Worth", "Qty") 
            output = box(tabulate(sorted_lst, headers=headers), lang="md")
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
