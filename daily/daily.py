import discord

from datetime import date, datetime, timedelta, timezone

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import humanize_number, humanize_timedelta

from redbot.core.bot import Red

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
            "daily_bar": [
                "<:Daily_left:783314575730147380>",
                "<:Daily_mid:783314575609036819>",
                "<:Daily_right:783314575784804373>",
            ],
            "midnight_today": "2020-01-01 00:00:00",
            "midnight_tomorrow": "2020-01-01 00:00:00",
        }

        default_guild = {"enabled": False, "credits": 100}

        default_member = {
            "credits": False,
            "messages": False,
            "fishing": False,
            "mining": False,
            "gambling": False,      
            "last_daily": "2020-01-01 00:00:00",
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
    async def daily1(self, ctx: commands.Context):
        """Runs the daily command for the user."""

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
            title="__**WORD**__",
            colour=await ctx.embed_colour(),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png")
        embed.set_author(
            name="AUTHOR NAME", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed.set_footer(text="Daily™ - Daily resets at 00:00 UTC")
        
        credits = memberdata["credits"]
        #Checks if last daily was yesterday.
        if last_daily < midnight_check:
            now = datetime.now(timezone.utc)
            now = now.strftime("%Y-%m-%d %H:%M:%S")
            await self.config.member(ctx.author).credits.set(True)
            await self.config.member(ctx.author).last_daily.set(now)
            credits = await self.config.guild(ctx.guild).credits()            
            currency_name = await bank.get_currency_name(ctx.guild)
            balance = humanize_number(int(await bank.get_balance(ctx.author)))
            remaining_time = str(now - midnight_tom_check)
            await bank.deposit_credits(ctx.author, credits)
            embed.description=f"You have earned {credits} {currency_name}.\nYou currently have {balance} {currency_name}.\nLEADERBOARD POSITION.\nYour next daily will be available in: {remaining_time}."
            await ctx.send(embed=embed)                        
        else:
            now = datetime.now(timezone.utc)
            now = now.replace(tzinfo=None)

            #now = now.strftime("%Y-%m-%d %H:%M:%S")
            remaining = int((midnight_tomorrow - now).total_seconds())
            remaining_time = str(timedelta(seconds=remaining))
            nice_remaining_time = datetime.strftime(remaining_time, "%H:%M:%S")
            embed.description=f"You have already claimed your daily.\nYour next daily will be available in: {nice_remaining_time}."
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
            if credits == False:
                embed.description += f"WRITE STUFF"
            else:
                embed.description += f"WRITE DIFFERENT STUFF"
               
