import discord
import time

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
            "last_quest": "2020-01-01 00:00:00",
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
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("This module is currently being worked on. Come back later!")  
        today = date.today()
        midnight_today = datetime.combine(today, datetime.min.time())        
        midnight_check = datetime.strptime(str(midnight_today), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_today.set(str(midnight_check))
        
        tomorrow = date.today() + timedelta(days=1)
        midnight_tomorrow = datetime.combine(tomorrow, datetime.min.time())
        midnight_tom_check = datetime.strptime(str(midnight_tomorrow), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_tomorrow.set(str(midnight_tom_check))
        
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
            await self.config.member(ctx.author).credits.set(True)
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
                
    @commands.command()
    @commands.guild_only()
    async def quests(self, ctx: commands.Context):
        """Shows the user their daily quests."""
        memberdata = await self.config.member(ctx.author).all()
        credits = memberdata["credits"]
        
        last_daily = datetime.strptime(str(memberdata["last_daily"]), "%Y-%m-%d %H:%M:%S")
        midnight_check = datetime.strptime(str(await self.config.midnight_today()), "%Y-%m-%d %H:%M:%S")
        
        if last_daily < midnight_check:
            await self.config.member(ctx.author).credits.set(False)
                        
        if credits == False:
            embed.description += f"WRITE STUFF"
        else:
            embed.description += f"WRITE DIFFERENT STUFF"
               
