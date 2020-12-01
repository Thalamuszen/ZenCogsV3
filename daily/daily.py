import discord

from datetime import date, datetime, timedelta

from redbot.core import Config, checks, commands, bank

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
        }

        default_guild = {"enabled": False, "cooldown": 30}

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
        """Toggle store for current server.
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

    @commands.command()
    @commands.guild_only()
    async def daily1(self, ctx: commands.Context):
        """Runs the daily command."""

        today = date.today()
        midnight_today = datetime.combine(today, datetime.min.time())        
        midnight_check = datetime.strptime(str(midnight_today), "%Y-%m-%d %H:%M:%S")
        await self.config.midnight_today.set(midnight_check)

        memberdata = await self.config.member(ctx.author).all()
        last_daily = datetime.strptime(str(userdata["last_daily"]), "%Y-%m-%d %H:%M:%S")
        
        if last_daily < midnight_check:
            await ctx.send(f"Midnight_today: {midnight_today}\nRun daily.")
        else:
            await ctx.send(f"Midnight_today: {midnight_today}\nCan't run daily.")
