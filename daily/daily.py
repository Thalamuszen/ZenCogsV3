import discord
import time

from random import uniform, randint
from datetime import date, datetime, timedelta, timezone

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import humanize_number, humanize_timedelta

from redbot.core.bot import Red

#Daily bar emojis.
BARDAILY = {
    "left_daily": "<:Daily_left:783314575730147380>",
    "mid_daily": "<:Daily_mid:783314575609036819>",
    "right_daily": "<:Daily_right:783314575784804373>",
}

#Empty bar emojis.
BAREMPTY = {
    "left_empty": "<:Empty_left:781138077354819584>",
    "mid_empty": "<:Empty_mid:781138077380771860>",
    "right_empty": "<:Empty_right:781138077380902932>",
}

class Daily(commands.Cog):
    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    __author__ = "ThalamusZen"
    __version__ = "0.6.9"    

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, 4119811374899, force_registration=True)

        default_global = {           
            "midnight_today": "2020-01-01 00:00:00",
            "midnight_tomorrow": "2020-01-01 00:00:00",
        }

        default_guild = {"enabled": False, "credits": 100}

        default_member = {
            "credits": False,
            "messages": False,
            "messages_quest": 0,
            "messages_count": 0,
            "messages_credits": 0,            
            "fishing": False,
            "fishing_quest": 0,
            "fishing_count": 0,
            "fishing_credits": 0,
            "mining": False,
            "mining_quest": 0,
            "mining_count": 0,
            "mining_credits": 0,
            "gambling": False,
            "gambling_quest": 0,
            "gambling_count": 0,
            "gambling_credits": 0,
            "last_daily": "2020-01-01 00:00:00",
            "quests_completed": "2020-01-01 00:00:00",
            "quests_built": "2020-01-01 00:00:00",
        }

        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def dailies(self, ctx):
        """Overall daily settings."""
        pass

    @dailies.command(name="toggle")
    async def dailies_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle dailies for current server.
        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).enabled())
        )
        await self.config.guild(ctx.guild).enabled.set(target_state)
        if target_state:
            await ctx.send("Dailies is now enabled.")
        else:
            await ctx.send("Dailies is now disabled.")

    @dailies.command(name="credits")
    async def dailies_credits(self, ctx: commands.Context, credits: int):
        """Change the amount of daily credits people will recieve."""
        currency_name = await bank.get_currency_name(ctx.guild)
        if credits <= 0:
            return await ctx.send("The amount of credits has to be more than 0.")
        else:
            await self.config.guild(ctx.guild).enabled.set(credits)
            await ctx.send("The daily amount of {currency_name} has been changed to {credits} per day.")

    @dailies.command(name="settings")
    async def dailies_settings(self, ctx: commands.Context):
        """Show all of the current settings."""
        enabled = await self.config.guild(ctx.guild).enabled()
        credits = await self.config.guild(ctx.guild).credits()
        await ctx.send(f"**Enabled:** {enabled}\n**Credits:** {credits}")          

    @commands.command()
    @commands.guild_only()
    async def daily(self, ctx: commands.Context):
        """Runs the daily command for the user."""
        
        #Checks if module enabled/disabled.
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("This module is currently being worked on. Come back later!") 
        
        #Update midnight values
        today = date.today()
        midnight_today = datetime.combine(today, datetime.min.time())        
        midnight_check = datetime.strptime(str(midnight_today), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_today.set(str(midnight_check))
        
        tomorrow = date.today() + timedelta(days=1)
        midnight_tomorrow = datetime.combine(tomorrow, datetime.min.time())
        midnight_tom_check = datetime.strptime(str(midnight_tomorrow), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_tomorrow.set(str(midnight_tom_check))
        
        #Data pull
        memberdata = await self.config.member(ctx.author).all()
        last_daily = datetime.strptime(str(memberdata["last_daily"]), "%Y-%m-%d %H:%M:%S")
        
        embed = discord.Embed(
            colour=await ctx.embed_colour(),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/783453482262331393.png")
        embed.set_author(
            name=f"{ctx.author.display_name}'s Daily Reward", icon_url=ctx.author.avatar_url,
        )
        embed.set_footer(text="Daily™ - Daily resets at 00:00 UTC")
        
        credits = memberdata["credits"]
        #Checks if last daily was yesterday.
        if last_daily < midnight_check:
            now = datetime.now(timezone.utc)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            now = now.replace(tzinfo=None)
            remaining = int((midnight_tomorrow - now).total_seconds())
            remaining_hour = time.strftime("%H", time.gmtime(remaining))
            remaining_hour = remaining_hour.lstrip("0")
            if remaining_hour == "":
                hour = ""
            elif remaining_hour == "1":
                hour = "hour,"
            else:
                hour = "hours,"            
            remaining_min = time.strftime("%M", time.gmtime(remaining))
            remaining_min = remaining_min.lstrip("0")
            if hour == "" and remaining_min == "":
                minute = ""
            elif remaining_hour == "1" and remaining_min == "":
                hour = "hour"
                minute = "and"
            elif remaining_hour > "1" and remaining_min == "":
                hour = "hours"
                minute = "and"                
            elif remaining_min == "":
                minute = "and"      
            elif remaining_min == "1":
                minute = "minute and"
            else:
                minute = "minutes and"                 
            remaining_sec = time.strftime("%S", time.gmtime(remaining))
            remaining_sec = remaining_sec.lstrip("0")
            if remaining_min == "" and remaining_sec == "":
                minute = ""
                second = ""
            elif remaining_min == "1" and remaining_sec == "":
                minute = "minute"
                second = ""
            elif remaining_min > "1" and remaining_sec == "":
                minute = "minutes"
                second = ""                
            elif remaining_min == "" and remaining_sec == "1":
                minute = ""
                second = "second"
            elif remaining_min == "" and remaining_sec > "1":
                minute = ""
                second = "seconds"                
            elif remaining_sec == "":
                second = ""
            elif remaining_sec == "1":
                second = "second"
            else:
                second = "seconds"            
            await self.config.member(ctx.author).credits.set(1)
            await self.config.member(ctx.author).last_daily.set(now_str)
            credits = await self.config.guild(ctx.guild).credits()            
            currency_name = await bank.get_currency_name(ctx.guild)
            balance = humanize_number(int(await bank.get_balance(ctx.author)))
            pos = await bank.get_leaderboard_position(ctx.author)
            await bank.deposit_credits(ctx.author, credits)
            balance = humanize_number(int(await bank.get_balance(ctx.author)))
            embed.title="__**Claimed Daily!**__"
            embed.description=f"You have earned **{credits}** {currency_name}.\nYou now have **{balance}** {currency_name}.\nYou are currently **#{pos}** on the global leaderboard!\nYour next daily will be available in:\n**{remaining_hour} {hour} {remaining_min} {minute} {remaining_sec} {second}**"
            await ctx.send(embed=embed)                        
        else:
            now = datetime.now(timezone.utc)
            now = now.replace(tzinfo=None)
            remaining = int((midnight_tomorrow - now).total_seconds())
            remaining_hour = time.strftime("%H", time.gmtime(remaining))
            remaining_hour = remaining_hour.lstrip("0")
            if remaining_hour == "":
                hour = ""
            elif remaining_hour == "1":
                hour = "hour,"
            else:
                hour = "hours,"
            remaining_min = time.strftime("%M", time.gmtime(remaining))
            remaining_min = remaining_min.lstrip("0")
            if hour == "" and remaining_min == "":
                minute = ""
            elif remaining_hour == "1" and remaining_min == "":
                hour = "hour"
                minute = "and"
            elif remaining_hour > "1" and remaining_min == "":
                hour = "hours"
                minute = "and"                
            elif remaining_min == "":
                minute = "and"      
            elif remaining_min == "1":
                minute = "minute and"
            else:
                minute = "minutes and"            
            remaining_sec = time.strftime("%S", time.gmtime(remaining))
            remaining_sec = remaining_sec.lstrip("0")
            if remaining_min == "" and remaining_sec == "":
                minute = ""
                second = ""
            elif remaining_min == "1" and remaining_sec == "":
                minute = "minute"
                second = ""
            elif remaining_min > "1" and remaining_sec == "":
                minute = "minutes"
                second = ""                   
            elif remaining_min == "" and remaining_sec == "1":
                minute = ""
                second = "second"
            elif remaining_min == "" and remaining_sec > "1":
                minute = ""
                second = "seconds"                
            elif remaining_sec == "":
                second = ""
            elif remaining_sec == "1":
                second = "second"
            else:
                second = "seconds"
            embed.title="__**Daily Already Claimed!**__"
            embed.description=f"You have already claimed your daily.\nYour next daily will be available in:\n**{remaining_hour} {hour} {remaining_min} {minute} {remaining_sec} {second}**"
            await ctx.send(embed=embed)
               
    @commands.command(aliases=["quest"])
    @commands.guild_only()
    async def quests(self, ctx: commands.Context):
        """Shows the user their daily quests."""
        
        #Checks if module enabled/disabled.
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("This module is currently being worked on. Come back later!") 
        
        #Update midnight values
        today = date.today()
        midnight_today = datetime.combine(today, datetime.min.time())        
        midnight_check = datetime.strptime(str(midnight_today), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_today.set(str(midnight_check))
        
        tomorrow = date.today() + timedelta(days=1)
        midnight_tomorrow = datetime.combine(tomorrow, datetime.min.time())
        midnight_tom_check = datetime.strptime(str(midnight_tomorrow), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_tomorrow.set(str(midnight_tom_check))
        
        #Data pull
        currency_name = await bank.get_currency_name(ctx.guild)        
        memberdata = await self.config.member(ctx.author).all()
        credits = memberdata["credits"]
        messages = memberdata["messages"]
        messages_quest = memberdata["messages_quest"]
        messages_count = memberdata["messages_count"]
        messages_credits = memberdata["messages_credits"]
        fishing = memberdata["fishing"]
        fishing_quest = memberdata["fishing_quest"]
        fishing_count = memberdata["fishing_count"]
        fishing_credits = memberdata["fishing_credits"]
                        
        last_daily = datetime.strptime(str(memberdata["last_daily"]), "%Y-%m-%d %H:%M:%S")
        quest_completed = datetime.strptime(str(memberdata["quest_completed"]), "%Y-%m-%d %H:%M:%S")
        quests_built = datetime.strptime(str(memberdata["quests_built"]), "%Y-%m-%d %H:%M:%S")
        midnight_check = datetime.strptime(str(await self.config.midnight_today()), "%Y-%m-%d %H:%M:%S")
        
        if last_daily < midnight_check:
            await self.config.member(ctx.author).credits.set(0)
        
        #Bar pull
        left_empty = BAREMPTY["left_empty"]
        mid_empty = BAREMPTY["mid_empty"]
        right_empty = BAREMPTY["right_empty"]
        left_full = BARDAILY["left_daily"]
        mid_full = BARDAILY["mid_daily"]
        right_full = BARDAILY["right_daily"]
        
        #Bar builder
        bar_empty = []
        bar_empty.append(left_empty)
        bar_empty.extend([mid_empty] * 8)
        bar_empty.append(right_empty)
        bar_empty = ''.join(bar_empty)
        
        bar_one = []
        bar_one.append(left_full)
        bar_one.extend([mid_empty] * 8)
        bar_one.append(right_empty)
        bar_one = ''.join(bar_one)
        
        bar_two = []
        bar_two.append(left_full)
        bar_two.extend([mid_full] * 1)
        bar_two.extend([mid_empty] * 7)
        bar_two.append(right_empty)
        bar_two = ''.join(bar_two)
        
        bar_three = []
        bar_three.append(left_full)
        bar_three.extend([mid_full] * 2)
        bar_three.extend([mid_empty] * 6)
        bar_three.append(right_empty)
        bar_three = ''.join(bar_three)
        
        bar_four = []
        bar_four.append(left_full)
        bar_four.extend([mid_full] * 3)
        bar_four.extend([mid_empty] * 5)
        bar_four.append(right_empty)
        bar_four = ''.join(bar_four) 
        
        bar_five = []
        bar_five.append(left_full)
        bar_five.extend([mid_full] * 4)
        bar_five.extend([mid_empty] * 4)
        bar_five.append(right_empty)
        bar_five = ''.join(bar_five) 
        
        bar_six = []
        bar_six.append(left_full)
        bar_six.extend([mid_full] * 5)
        bar_six.extend([mid_empty] * 3)
        bar_six.append(right_empty)
        bar_six = ''.join(bar_six)
        
        bar_seven = []
        bar_seven.append(left_full)
        bar_seven.extend([mid_full] * 6)
        bar_seven.extend([mid_empty] * 2)
        bar_seven.append(right_empty)
        bar_seven = ''.join(bar_seven)
        
        bar_eight = []
        bar_eight.append(left_full)
        bar_eight.extend([mid_full] * 7)
        bar_eight.extend([mid_empty] * 1)
        bar_eight.append(right_empty)
        bar_eight = ''.join(bar_eight)
        
        bar_nine = []
        bar_nine.append(left_full)
        bar_nine.extend([mid_full] * 8)
        bar_nine.append(right_empty)
        bar_nine = ''.join(bar_nine)
        
        bar_full = []
        bar_full.append(left_full)
        bar_full.extend([mid_full] * 8)
        bar_full.append(right_full)
        bar_full = ''.join(bar_full)         
        
        #Quest builder. If Quest was completeted or not. Build new quest. Overwrite values on new day.
        if quests_built < midnight_check:
            await self.config.member(ctx.author).messages.set(0)
            messages_quest_total = int(randint(10, 25))
            await self.config.member(ctx.author).messages_quest.set(messages_quest_total)
            await self.config.member(ctx.author).messages_count.set(0)
            messages_quest_credits = messages_quest_total * 10
            await self.config.member(ctx.author).messages_credits.set(messages_quest_credits)
            
            await self.config.member(ctx.author).fishing.set(0)
            fishing_quest_total = int(randint(10, 25))
            await self.config.member(ctx.author).fishing_quest.set(fishing_quest_total)
            await self.config.member(ctx.author).fishing_count.set(0)
            fishing_quest_credits = fishing_quest_total * 10
            await self.config.member(ctx.author).fishing_credits.set(fishing_quest_credits)
            
            now = datetime.now(timezone.utc)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            await self.config.member(ctx.author).quests_built.set(now_str)
        #Grabs the values from the quest builder as there is a delay between writing and reading.
        try:
            fishing_quest = fishing_quest_total
            fishing_count = 0
            fishing_credits = fishing_quest_credits
        except:
            pass
        #Embed builder            
        embed = discord.Embed(
            colour=await ctx.embed_colour(),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/783453482262331393.png")
        embed.set_author(
            name=f"{ctx.author.display_name}'s Daily Quests", icon_url=ctx.author.avatar_url,
        )
        embed.description = "**Completion Status**\n\n"
        embed.set_footer(text="Questy™ - Quests reset at 00:00 UTC")
        
        #Embed daily
        credits = memberdata["credits"]                      
        if credits == False:
            embed.description += "**Daily** You haven't claimed your daily yet.\n\n"
        else:
            embed.description += "**Daily** Daily Claimed.\n\n"
        
        #Embed fishing calculator
        per_bar = float(fishing_quest / 10)
        tier_one = per_bar
        tier_two = per_bar * 2
        tier_three = per_bar * 3
        tier_four = per_bar * 4
        tier_five = per_bar * 5
        tier_six = per_bar * 6
        tier_seven = per_bar * 7
        tier_eight = per_bar * 8
        tier_nine = per_bar * 9
        tier_ten = per_bar * 10
        
        fishing_count = memberdata["fishing_count"]                                      
        if fishing_count == 0:
            fishing_bar = bar_empty
        elif 0 < fishing_count <= tier_one:
            fishing_bar = bar_one
        elif tier_one < fishing_count <= tier_two:
            fishing_bar = bar_two
        elif tier_two < fishing_count <= tier_three:
            fishing_bar = bar_three
        elif tier_three < fishing_count <= tier_four:
            fishing_bar = bar_four
        elif tier_four < fishing_count <= tier_five:
            fishing_bar = bar_five
        elif tier_five < fishing_count <= tier_six:
            fishing_bar = bar_six
        elif tier_six < fishing_count <= tier_seven:
            fishing_bar = bar_seven
        elif tier_seven < fishing_count <= tier_eight:
            fishing_bar = bar_eight
        elif tier_eight < fishing_count <= tier_nine:
            fishing_bar = bar_nine 
        elif tier_nine < fishing_count < tier_ten:
            fishing_bar = bar_nine
        elif fishing_count >= tier_ten:
            fishing_bar = bar_full
        
        #Embed fishing
        fishing = memberdata["fishing"]
        fishing_quest = memberdata["fishing_quest"]
        fishing_count = memberdata["fishing_count"]
        fishing_credits = memberdata["fishing_credits"]
        #Stops the fishing count going over the quest amount.
        if fishing_count > fishing_quest:
            fishing_count = fishing_quest
        #Works out which description to send use
        if fishing_count == fishing_quest:
            if fishing == False:
                await bank.deposit_credits(ctx.author, credits)
            await self.config.member(ctx.author).fishing.set(1)    
            embed.description += f"**Catch {fishing_quest} fish** - **Completed!**\n{fishing_bar} {fishing_count}/{fishing_quest}\n**Reward:** {fishing_credits} {currency_name}"
        else:
            embed.description += f"**Catch {fishing_quest} fish**\n{fishing_bar} {fishing_count}/{fishing_quest}\n**Reward:** {fishing_credits} {currency_name}"
            
        #All quests complete bonus
        #if messages = memberdata["messages"]
            #if fishing = memberdata["fishing"]
        #Above all of the above pulls true, give reward.
        
        #Embed send                              
        await ctx.send(embed=embed)
               
