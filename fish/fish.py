import asyncio
import datetime
import discord
import logging
import random

from random import uniform, randint
from discord.utils import get
from datetime import date, datetime, timedelta, timezone
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
    "\ud83d\udc5e": "trash",
    "\ud83d\udc5f": "trash",
    "\ud83e\udd7e": "trash",
    "\ud83d\udc60": "trash",
    "\ud83e\uddf2": "trash",
    "\ud83e\udde6": "trash",
    "\ud83d\udc20": "uncommon",
    "\ud83d\udc21": "uncommon",
    "<:FactorioFish:782613249476395019>": "uncommon",
    "<:Narwhal:782618975170986034>": "uncommon",
    "\ud83d\udc1f": "common",
    "\ud83e\udd80": "common",
    "\ud83e\udd90": "common",
}
RARES = {
    "\ud83d\udc22": "Turtle",
    "\ud83d\udc33": "Blow whale",
    "\ud83d\udc0b": "Whale",
    "\ud83d\udc0a": "Crocodile",
    "\ud83d\udc27": "Penguin",
    "\ud83d\udc19": "Octopus",
    "\ud83e\udd88": "Shark",      
    "\ud83e\udd91": "Squid",  
    "\ud83d\udc2c": "Dolphin",
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
                "\ud83d\udc5e",
                "\ud83d\udc5f",
                "\ud83e\udd7e",
                "\ud83d\udc60",
                "\ud83e\uddf2",
                "\ud83e\udde6",
            ],
            "uncommon": [
                "\ud83d\udc20",
                "\ud83d\udc21",
                "<:FactorioFish:782613249476395019>",
                "<:Narwhal:782618975170986034>",
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
        """Reset someones Trophy room."""
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
        casting_price = 5
        balance = int(await bank.get_balance(ctx.author))
        credits_name = await bank.get_currency_name(ctx.guild)        
        if casting_price > balance:
            return await ctx.send(f"It cost's {casting_price} {credits_name} to buy bait. You don't have enough!")
        author = ctx.message.author
        userdata = await self.config.user(ctx.author).all()
        last_time = datetime.strptime(str(userdata["last_fish"]), "%Y-%m-%d %H:%M:%S.%f")
        now = datetime.now(timezone.utc)
        now = now.replace(tzinfo=None)
        seconds = int((now - last_time).total_seconds())
        cd = await self.config.guild(ctx.guild).cooldown()
        secs = cd - seconds
        if int((now - last_time).total_seconds()) < await self.config.guild(ctx.guild).cooldown():
            return await ctx.send(f"<:Fishing:782681118674780200> **| {author.name} you can fish again in {secs} seconds.**", delete_after=secs)
        await self.config.user(ctx.author).last_fish.set(str(now))            
        await bank.withdraw_credits(ctx.author, casting_price)
        
        #Daily cog input.
        memberdata = await self.bot.get_cog("Daily").config.member(ctx.author).all()
        fishing = memberdata["fishing"]
        fishing_count = memberdata["fishing_count"]
        fishing_quest = memberdata["fishing_quest"]
        fishing_credits = memberdata["fishing_credits"]
        #Update midnight values
        today = date.today()
        midnight_today = datetime.combine(today, datetime.min.time())        
        midnight_check = datetime.strptime(str(midnight_today), "%Y-%m-%d %H:%M:%S")
        await self.bot.get_cog("Daily").config.midnight_today.set(str(midnight_check))
        #Pull when their last quest was built
        quests_built = datetime.strptime(str(memberdata["quests_built"]), "%Y-%m-%d %H:%M:%S")   
        
        chance = uniform(0, 99)
        rarechance = 0.15
        uncommonchance = 10.15
        commonchance = 74

        if chance <= rarechance:
            rarefish = await self.config.rarefish()
#            mn = len(rarefish)
#            r = randint(0, mn - 1)
#            fish = rarefish[r]
            fish = (random.choice(rarefish))            
            item = RARES[fish]
            await ctx.send(
                (
                    "<:Fishing:782681118674780200> **| {author.name}** caught a **{item}**, it's **rare!!! |** {fish}\n"
                    "Type `!rarefish` to see your trophy room"
                ).format(
                    author=author,
                    item=item,
                    fish=fish,
                )
            )
            #Fishing module quest check/completion
            await self.bot.get_cog("Daily").config.member(ctx.author).fishing_count.set(fishing_count + 1)
            fishing_count = fishing_count + 1            
            if fishing_count == fishing_quest:
                if quests_built < midnight_check:
                    pass
                elif fishing == False:
                    credits = int(fishing_credits)
                    await bank.deposit_credits(ctx.author, credits)
                    await ctx.send(f"<:Coins:783453482262331393> **| Fishing quest complete!**\n<:Coins:783453482262331393> **| Reward:** {fishing_credits} {credits_name}")
                await self.bot.get_cog("Daily").config.member(ctx.author).fishing.set(1)              
            try:
                item = RARES[fish]
                fish_info = await self.bot.get_cog("Shop").config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(fish_info.get("quantity"))
                author_quantity += 1
                await self.bot.get_cog("Shop").config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)
                if item == "Turtle":
                    await self.config.user(ctx.author).turtle.set(userdata["turtle"] + 1)
                elif item == "Blow whale":
                    await self.config.user(ctx.author).blow_whale.set(userdata["blow_whale"] + 1)
                elif item == "Whale":
                    await self.config.user(ctx.author).whale.set(userdata["whale"] + 1)  
                elif item == "Crocodile":
                    await self.config.user(ctx.author).crocodile.set(userdata["crocodile"] + 1)
                elif item == "Penguin":
                    await self.config.user(ctx.author).penguin.set(userdata["penguin"] + 1)
                elif item == "Octopus":
                    await self.config.user(ctx.author).octopus.set(userdata["octopus"] + 1)   
                elif item == "Shark":
                    await self.config.user(ctx.author).shark.set(userdata["shark"] + 1)  
                elif item == "Squid":
                    await self.config.user(ctx.author).squid.set(userdata["squid"] + 1) 
                elif item == "Dolphin":
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
                if item == "Turtle":
                    await self.config.user(ctx.author).turtle.set(userdata["turtle"] + 1)
                elif item == "Blow whale":
                    await self.config.user(ctx.author).blow_whale.set(userdata["blow_whale"] + 1)   
                elif item == "Whale":
                    await self.config.user(ctx.author).whale.set(userdata["whale"] + 1)  
                elif item == "Crocodile":
                    await self.config.user(ctx.author).crocodile.set(userdata["crocodile"] + 1)
                elif item == "Penguin":
                    await self.config.user(ctx.author).penguin.set(userdata["penguin"] + 1)
                elif item == "Octopus":
                    await self.config.user(ctx.author).octopus.set(userdata["octopus"] + 1)   
                elif item == "Shark":
                    await self.config.user(ctx.author).shark.set(userdata["shark"] + 1)  
                elif item == "Squid":
                    await self.config.user(ctx.author).squid.set(userdata["squid"] + 1) 
                elif item == "Dolphin":
                    await self.config.user(ctx.author).dolphin.set(userdata["dolphin"] + 1)                     
        elif rarechance < chance <= uncommonchance:
            uncommon = await self.config.uncommon()
#            mn = len(uncommon)
#            u = randint(0, mn - 1)
#            fish = uncommon[u]
            fish = (random.choice(uncommon))            
            await ctx.send(f"<:Fishing:782681118674780200> **| {author.name}** caught an **uncommon fish! |** {fish}")
            #Fishing module quest check/completion
            await self.bot.get_cog("Daily").config.member(ctx.author).fishing_count.set(fishing_count + 1)
            fishing_count = fishing_count + 1
            if fishing_count == fishing_quest:
                if quests_built < midnight_check:
                    pass                
                elif fishing == False:                    
                    credits = int(fishing_credits)
                    await bank.deposit_credits(ctx.author, credits)
                    await ctx.send(f"<:Coins:783453482262331393> **| Fishing quest complete!**\n<:Coins:783453482262331393> **| Reward:** {fishing_credits} {credits_name}")
                await self.bot.get_cog("Daily").config.member(ctx.author).fishing.set(1)           
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
#            mn = len(common)
#            c = randint(0, mn - 1)
#            fish = common[c]
            fish = (random.choice(common))            
            await ctx.send(f"<:Fishing:782681118674780200> **| {author.name}** caught a **common fish |** {fish}")
            #Fishing module quest check/completion
            await self.bot.get_cog("Daily").config.member(ctx.author).fishing_count.set(fishing_count + 1)
            fishing_count = fishing_count + 1
            if fishing_count == fishing_quest:
                if quests_built < midnight_check:
                    pass                  
                elif fishing == False:
                    credits = int(fishing_credits)
                    await bank.deposit_credits(ctx.author, credits)
                    await ctx.send(f"<:Coins:783453482262331393> **| Fishing quest complete!**\n<:Coins:783453482262331393> **| Reward:** {fishing_credits} {credits_name}")
                await self.bot.get_cog("Daily").config.member(ctx.author).fishing.set(1)          
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
#            mn = len(trash)
#            t = randint(0, mn - 1)
#            fish = trash[t]
            fish = (random.choice(trash))
            await ctx.send(f"<:Fishing:782681118674780200> **| {author.name}** caught a piece of **trash |** {fish}")
            #Fishing module quest check/completion
            await self.bot.get_cog("Daily").config.member(ctx.author).fishing_count.set(fishing_count + 1)
            fishing_count = fishing_count + 1
            if fishing_count == fishing_quest:
                if quests_built < midnight_check:
                    pass                
                elif fishing == False:
                    credits = int(fishing_credits)
                    await bank.deposit_credits(ctx.author, credits)
                    await ctx.send(f"<:Coins:783453482262331393> **| Fishing quest complete!**\n<:Coins:783453482262331393> **| Reward:** {fishing_credits} {credits_name}")
                await self.bot.get_cog("Daily").config.member(ctx.author).fishing.set(1)           
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
        """Shows which rares you have caught and how many."""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the lake is closed. Come back later!")
        userdata = await self.config.user(ctx.author).all()
        em = discord.Embed(color=await ctx.embed_color(), timestamp=datetime.now())
        em.title = f"{ctx.author.name}'s Rare Trophy Wall"      
        em.set_thumbnail(url="https://cdn.discordapp.com/attachments/777176220378071050/777218030501363752/fishingsquare.gif") 
        em.description = f"Here you can see all of the rares you have caught.\nThere are **nine** rares to find in the lake, can you\n catch them all?\n**Happy Fishing!**\n\n"     
        if userdata["turtle"]:
            number = userdata['turtle']
            em.description += f"\N{TURTLE} x**{userdata['turtle']}** - Turtle\n"
        if userdata["blow_whale"]:
            number = userdata['blow_whale']
            em.description += f"\N{SPOUTING WHALE} x**{userdata['blow_whale']}** - Blow Whale\n"
        if userdata["whale"]:
            number = userdata['whale']
            em.description += f"\N{WHALE} x**{userdata['whale']}** - Whale\n"
        if userdata["crocodile"]:
            number = userdata['crocodile']
            em.description += f"\N{CROCODILE} x**{userdata['crocodile']}** - Crocodile\n"          
        if userdata["penguin"]:
            number = userdata['penguin']
            em.description += f"\N{PENGUIN} x**{userdata['penguin']}** - Penguin\n"            
        if userdata["octopus"]:
            number = userdata['octopus']
            em.description += f"\N{OCTOPUS} x**{userdata['octopus']}** - Octopus\n"   
        if userdata["shark"]:
            number = userdata['shark']
            em.description += f"\N{SHARK} x**{userdata['shark']}** - Shark\n"  
        if userdata["squid"]:
            number = userdata['squid']
            em.description += f"\N{SQUID} x**{userdata['squid']}** - Squid\n"            
        if userdata["dolphin"]:
            number = userdata['dolphin']
            em.description += f"\N{DOLPHIN} x**{userdata['dolphin']}** - Dolphin\n"       
        em.set_footer(text="Fishy™")            
        await ctx.send(embed=em)  

    @commands.command()
    @commands.guild_only()
    async def net(self, ctx: commands.Context):
        """Shows what you have caught from the lake and how many."""        
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
