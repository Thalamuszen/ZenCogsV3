import asyncio
import discord
import random

from typing import Union, Optional
from discord.utils import get
from datetime import datetime
from tabulate import tabulate
from operator import itemgetter

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import pagify, humanize_list, humanize_number, box
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

from redbot.core.bot import Red


class Shop(commands.Cog):
    """
    Standalone Shop Cog.
    """

    __author__ = "ThalamusZen"
    __version__ = "0.6.9"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=16548964843212315, force_registration=True
        )
        self.config.register_guild(
            enabled=False, xmasshop=False, items={}, roles={}, games={}, xmas={}, ping=None
        )
        self.config.register_member(inventory={})

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def store(self, ctx):
        """Overall store settings."""
        pass

    @store.command(name="toggle")
    async def store_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle store for current server.
        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).enabled())
        )
        await self.config.guild(ctx.guild).enabled.set(target_state)
        if target_state:
            await ctx.send("Store is now enabled.")
        else:
            await ctx.send("Store is now disabled.")
	
    @store.command(name="xmastoggle")
    async def xmas_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle the Xmas shop for current server.
        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).xmasshop())
        )
        await self.config.guild(ctx.guild).xmasshop.set(target_state)
        if target_state:
            await ctx.send("The Xmas shop is now enabled.")
        else:
            await ctx.send("The Xmas shop is now disabled.")	

    @store.command(name="add")
    async def store_add(self, ctx: commands.Context):
        """Add a buyable item/role/game key."""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        types = ["item", "role", "game", "xmas"]
        pred = MessagePredicate.lower_contained_in(types)
        pred_int = MessagePredicate.valid_int(ctx)
        pred_role = MessagePredicate.valid_role(ctx)
        pred_yn = MessagePredicate.yes_or_no(ctx)

        await ctx.send(
            "Do you want to add an item, role, game or xmas?\nItem and role = returnable, game and xmas = non returnable."
        )
        try:
            await self.bot.wait_for("message", timeout=30, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        if pred.result == 0:
            await ctx.send(
                "What is the name of the item? Note that you cannot include `@` in the name."
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            item_name = answer.content
            item_name = item_name.strip("@")
            try:
                is_already_item = await self.config.guild(ctx.guild).items.get_raw(
                    item_name
                )
                if is_already_item:
                    return await ctx.send(
                        "This item is already set. Please, remove it first."
                    )
            except KeyError:
                await ctx.send("How much should this item cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")
                await ctx.send("What quantity of this item should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
                await ctx.send("Is the item redeemable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                redeemable = pred_yn.result
                await ctx.send("Give the item a description")
                try:
                    answer = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                description = answer.content
                description = description.strip("@")				
                await self.config.guild(ctx.guild).items.set_raw(
                    item_name,
                    value={
                        "price": price,
                        "quantity": quantity,
                        "redeemable": redeemable,
			"description": description,			    
                    },
                )
                await ctx.send(f"{item_name} added.")
        elif pred.result == 1:
            await ctx.send("What is the role? (Must be a role that exists on the server)")
            try:
                await self.bot.wait_for("message", timeout=30, check=pred_role)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            role = pred_role.result
            try:
                is_already_role = await self.config.guild(ctx.guild).roles.get_raw(
                    role.name
                )
                if is_already_role:
                    return await ctx.send(
                        "This item is already set. Please, remove it first."
                    )
            except KeyError:
                await ctx.send("How much should this role cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")
                await ctx.send("What quantity of this item should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
                await ctx.send(
                    "What is the friendly name of the role?"
                )
                try:
                    answer = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                safe_name = answer.content
                safe_name = safe_name.strip("@")
                await self.config.guild(ctx.guild).roles.set_raw(
                    safe_name, value={"price": price, "quantity": quantity, "role_name": role.name}
                )
                await ctx.send(f"{role.name} added.")
        elif pred.result == 2:
            await ctx.send(
                "What is the name of the game? Note that you cannot include `@` in the name."
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            game_name = answer.content
            game_name = game_name.strip("@")
            try:
                is_already_game = await self.config.guild(ctx.guild).games.get_raw(
                    game_name
                )
                if is_already_game:
                    return await ctx.send(
                        "This item is already set. Please, remove it first."
                    )
            except KeyError:
                await ctx.send("How much should this game cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")
                await ctx.send("What quantity of this item should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
                await ctx.send("Is the item redeemable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                redeemable = pred_yn.result
                await self.config.guild(ctx.guild).games.set_raw(
                    game_name,
                    value={
                        "price": price,
                        "quantity": quantity,
                        "redeemable": redeemable,
                    },
                )
                await ctx.send(f"{game_name} added.")
        if pred.result == 3:
            await ctx.send(
                "What is the name of the xmas gift? Note that you cannot include `@` in the name."
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            xmas_gift = answer.content
            xmas_gift = xmas_gift.strip("@")
            try:
                is_already_xmas = await self.config.guild(ctx.guild).xmas.get_raw(
                    xmas_gift
                )
                if is_already_xmas:
                    return await ctx.send(
                        "This xmas gift is already set. Please, remove it first."
                    )
            except KeyError:
                await ctx.send("How much should this xmas gift cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")
                await ctx.send("What is the gift category? Lowercase only. (card/sf/cp/ch/lp)")
                try:
                    answer = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                size = answer.content
                size = size.strip("@")		
                await ctx.send("What quantity of this xmas gift should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
                await ctx.send("Is the item redeemable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                redeemable = pred_yn.result
                await self.config.guild(ctx.guild).xmas.set_raw(
                    xmas_gift,
                    value={
                        "price": price,
                        "quantity": quantity,
                        "redeemable": redeemable,
                        "giftable": True,
                        "gifted": False,
			"size": size,			    
                    },
                )
                await ctx.send(f"{xmas_gift} added.")
        else:
            await ctx.send("This answer is not supported. Try again, please.")

    @store.command(name="remove")
    async def store_remove(self, ctx: commands.Context, *, item: str):
        """Remove a buyable item/role/game key."""
        item = item.strip("@")
        try:
            is_already_item = await self.config.guild(ctx.guild).items.get_raw(item)
            if is_already_item:
                await self.config.guild(ctx.guild).items.clear_raw(item)
                return await ctx.send(f"{item} removed.")
        except KeyError:
            try:
                is_already_game = await self.config.guild(ctx.guild).games.get_raw(item)
                if is_already_game:
                    await self.config.guild(ctx.guild).games.clear_raw(item)
                    return await ctx.send(f"{item} removed.")
            except KeyError:
                try:
                    is_already_role = await self.config.guild(ctx.guild).roles.get_raw(
                        item
                    )
                    if is_already_role:
                        await self.config.guild(ctx.guild).roles.clear_raw(item)
                        await ctx.send(f"{item} removed.")
                except KeyError:
                    try:
                        is_already_xmas = await self.config.guild(ctx.guild).xmas.get_raw(item)
                        if is_already_xmas:
                            await self.config.guild(ctx.guild).xmas.clear_raw(item)
                            return await ctx.send(f"{item} removed.")
                    except KeyError:
                        await ctx.send("That item isn't buyable.")

    @store.command(name="show")
    async def store_show(self, ctx: commands.Context, *, item: str):
        """Show information about a buyable item/role/game key."""
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()

        if item in items:
            info = await self.config.guild(ctx.guild).items.get_raw(item)
            item_type = "item"
        elif item in roles:
            info = await self.config.guild(ctx.guild).roles.get_raw(item)
            item_type = "role"
        elif item in games:
            info = await self.config.guild(ctx.guild).games.get_raw(item)
            item_type = "game"
        elif item in xmas:
            info = await self.config.guild(ctx.guild).xmas.get_raw(item)
            item_type = "xmas"            
        else:
            return await ctx.send("This item isn't buyable.")
        price = info.get("price")
        quantity = info.get("quantity")
        redeemable = info.get("redeemable")
        description = info.get("description")
        size = info.get("size")
        if not redeemable:
            redeemable = False
        await ctx.send(
            f"**__{item}:__**\n**Type:** {item_type}\n**Price:** {price}\n**Quantity:** {quantity}\n**Redeemable:** {redeemable}\n**Description:** {description}\n**Xmas gift size:** {size}"
        )

    @store.command(name="price")
    async def store_price(self, ctx: commands.Context, price: int, *, item: str):
        """Change the price of an existing buyable item."""
        if price <= 0:
            return await ctx.send("Uh oh, price has to be more than 0.")
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()

        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(item, "price", value=price)
            await ctx.send(f"{item}'s price changed to {price}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(item, "price", value=price)
            await ctx.send(f"{item}'s price changed to {price}.")
        elif item in games:
            await self.config.guild(ctx.guild).games.set_raw(item, "price", value=price)
            await ctx.send(f"{item}'s price changed to {price}.")
        elif item in xmas:
            await self.config.guild(ctx.guild).xmas.set_raw(item, "price", value=price)
            await ctx.send(f"{item}'s price changed to {price}.")            
        else:
            await ctx.send("This item isn't in the store. Please, add it first.")                               
            
    @store.command(name="quantity")
    async def store_quantity(self, ctx: commands.Context, quantity: int, *, item: str):
        """Change the quantity of an existing buyable item."""
        if quantity <= 0:
            return await ctx.send("Uh oh, quantity has to be more than 0.")
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()

        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(
                item, "quantity", value=quantity
            )
            await ctx.send(f"{item}'s quantity changed to {quantity}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(
                item, "quantity", value=quantity
            )
            await ctx.send(f"{item}'s quantity changed to {quantity}.")
        elif item in games:
            await self.config.guild(ctx.guild).games.set_raw(
                item, "quantity", value=quantity
            )
            await ctx.send(f"{item}'s quantity changed to {quantity}.")
        elif item in xmas:
            await self.config.guild(ctx.guild).xmas.set_raw(
                item, "quantity", value=quantity
            )
            await ctx.send(f"{item}'s quantity changed to {quantity}.")            
        else:
            await ctx.send("This item isn't in the store. Please, add it first.")

    @store.command(name="description")
    async def store_description(self, ctx: commands.Context, *, item: str):
        """Change the description of an existing buyable item."""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        item = item.strip("@")
        items = await self.config.guild(ctx.guild).items.get_raw()
        if item in items:
            await ctx.send(
                "What would you like to change the description to?"
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            description = answer.content
            await self.config.guild(ctx.guild).items.set_raw(
                item, "description", value=description
            )
            await ctx.send(f"{item}'s description has been changed.")       
        else:
            await ctx.send("This item isn't in the store. Please, add it first.")

    @store.command(name="redeemable")
    async def store_redeemable(
        self, ctx: commands.Context, redeemable: bool, *, item: str
    ):
        """Change the redeemable of an existing buyable item."""
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()        

        item = item.strip("@")
        if item in items:
            await self.config.guild(ctx.guild).items.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"{item}'s redeemability changed to {redeemable}.")
        elif item in roles:
            await self.config.guild(ctx.guild).roles.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"{item}'s redeemability changed to {redeemable}.")
        elif item in games:
            await self.config.guild(ctx.guild).games.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"{item}'s redeemability changed to {redeemable}.")
        elif item in xmas:
            await self.config.guild(ctx.guild).xmas.set_raw(
                item, "redeemable", value=redeemable
            )
            await ctx.send(f"{item}'s redeemability changed to {redeemable}.")            
        else:
            await ctx.send("This item isn't in the store. Please, add it first.")

    @store.command(name="reset")
    async def store_reset(self, ctx: commands.Context, confirmation: bool = False):
        """Delete all items from the store."""
        if not confirmation:
            return await ctx.send(
                "This will delete **all** items. This action **cannot** be undone.\n"
                f"If you're sure, type `{ctx.clean_prefix}store reset yes`."
            )
        for i in await self.config.guild(ctx.guild).items.get_raw():
            await self.config.guild(ctx.guild).items.clear_raw(i)
        for r in await self.config.guild(ctx.guild).roles.get_raw():
            await self.config.guild(ctx.guild).roles.clear_raw(r)
        for g in await self.config.guild(ctx.guild).games.get_raw():
            await self.config.guild(ctx.guild).games.clear_raw(g)
        for x in await self.config.guild(ctx.guild).xmas.get_raw():
            await self.config.guild(ctx.guild).xmas.clear_raw(x)            
        await ctx.send("All items have been deleted from the store.")

    @store.command(name="ping")
    async def store_ping(
        self, ctx: commands.Context, who: Union[discord.Member, discord.Role] = None
    ):
        """Set the role/member that should be pinged when a member wants to redeem their item.
        If who isn't provided, it will show the current ping set."""
        if not who:
            ping_id = await self.config.guild(ctx.guild).ping()
            if not ping_id:
                return await ctx.send("No ping is set.")
            ping = get(ctx.guild.members, id=ping_id)
            if not ping:
                ping = get(ctx.guild.roles, id=ping_id)
                if not ping:
                    return await ctx.send(
                        "The role must have been deleted or user must have left."
                    )
            return await ctx.send(f"{ping.name} is set to be pinged.")
        await self.config.guild(ctx.guild).ping.set(who.id)
        await ctx.send(
            f"{who.name} has been set to be pinged when a member wants to redeem their item."
        )

    @store.command(name="resetinventories")
    async def store_resetinventories(
        self, ctx: commands.Context, confirmation: bool = False
    ):
        """Delete all items from all members' inventories."""
        if not confirmation:
            return await ctx.send(
                "This will delete **all** items from all members' inventories. This action **cannot** be undone.\n"
                f"If you're sure, type `{ctx.clean_prefix}store resetinventories yes`."
            )
        for member in ctx.guild.members:
            inventory = await self.config.member(member).inventory.get_raw()
            for item in inventory:
                await self.config.member(member).inventory.clear_raw(item)
        await ctx.send("All items have been deleted from all members' inventories.")

    @commands.command()
    @commands.guild_only()
    async def shop(self, ctx: commands.Context, page: Optional[str] = ""):
        """Display the shop."""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")
        #page = "roles"
        await self._show_store(ctx, page)

    @commands.command()
    @commands.guild_only()
    async def buy(self, ctx: commands.Context, quantity: Optional[int] = 1, *, item: str = ""):      
        """Buy an item from the shop."""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")
        balance = int(
            await bank.get_balance(ctx.author)
        )
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()
        # Catch all. Including the removal of s at the end of multiples.
        item = item.lower()
        item = item.strip("@")
        if item in items:
            pass
        elif item in roles:
            pass
        elif item in games:
            pass
        elif item in xmas:
            pass
        else:
            item = item[:-1]
        #end
        inventory = await self.config.member(ctx.author).inventory.get_raw()            
        if item in roles:
            if item in inventory:
                return await ctx.send("You already own this role.")
            if quantity > 1:
                return await ctx.send("You can only buy one of each role.")
            info = await self.config.guild(ctx.guild).roles.get_raw(item)
            role_name = info.get("role_name")
            role_obj = get(ctx.guild.roles, name=role_name)
            if role_obj:
                role = await self.config.guild(ctx.guild).roles.get_raw(item)
                price = int(role.get("price"))
                pricenice = humanize_number(price) 
                quantityinstock = int(role.get("quantity"))
                credits_name = await bank.get_currency_name(ctx.guild)
                if quantityinstock == 0:
                    return await ctx.send("Uh oh, this item is out of stock.")
                if price <= balance:
                    pass
                else:
                    return await ctx.send(f"You don't have enough {credits_name}! This item costs {pricenice} {credits_name}")
                await ctx.author.add_roles(role_obj)
                balance -= price
                quantityinstock -= quantity
                await bank.withdraw_credits(ctx.author, price)
                await self.config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": quantity,  
                        "is_item": False,
                        "is_role": True,
                        "is_game": False,
                        "is_xmas": False,
                        "redeemable": False,
                        "redeemed": False,
                        "giftable": False,
                        "gifted": False,                         
                    },
                )
                await self.config.guild(ctx.guild).roles.set_raw(
                    item, "quantity", value=quantityinstock
                )
                await ctx.send(f"You have bought {quantity} {item}(s) for {pricenice} {credits_name}.")
            else:
                await ctx.send("Uh oh, can't find the role.")
        elif item in items:
            item_info = await self.config.guild(ctx.guild).items.get_raw(item)
            price = int(item_info.get("price"))
            totalcost = price * quantity
            totalcostnice = humanize_number(totalcost)
            description = item_info.get("description")
            quantityinstock = int(item_info.get("quantity"))
            credits_name = await bank.get_currency_name(ctx.guild)
            redeemable = item_info.get("redeemable")
            if not redeemable:
                redeemable = False
            if quantityinstock == 0:
                return await ctx.send("Uh oh, this item is out of stock.")
            if quantityinstock < quantity:
                return await ctx.send("Uh oh, there isn't enough in stock!")
            if totalcost <= balance:
                pass
            else:
                return await ctx.send(f"You don't have enough {credits_name}! You need {totalcostnice} {credits_name} to buy {quantity} {item}(s)")
            try:
                info = await self.config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(info.get("quantity"))                
                balance -= price * quantity
                quantityinstock -= quantity
                await bank.withdraw_credits(ctx.author, totalcost)
                await self.config.guild(ctx.guild).items.set_raw(
                    item, "quantity", value=quantityinstock
                )       
                if not redeemable:
                    author_quantity += quantity
                    await self.config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)               
                    await ctx.send(f"You have bought {quantity} {item}(s) for {totalcostnice} {credits_name}.")
                else:
                    author_quantity += quantity
                    await self.config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)                                
                    await ctx.send(
                        f"You have bought {quantity} {item}(s). You may now redeem it with `{ctx.clean_prefix}redeem {item}`"
                    )
            except KeyError:
                balance -= price * quantity
                quantityinstock -= quantity
                await bank.withdraw_credits(ctx.author, totalcost)
                await self.config.guild(ctx.guild).items.set_raw(
                    item, "quantity", value=quantityinstock
                )
                if not redeemable:
                    await self.config.member(ctx.author).inventory.set_raw(
                        item,
                        value={
                            "price": price,
                            "quantity": quantity,
                            "is_item": True,                        
                            "is_role": False,
                            "is_game": False,
                            "is_xmas": False,
                            "redeemable": False,
                            "redeemed": True,
                            "description": description,				
                            "giftable": False,
                            "gifted": False,                         
                        },
                    )
                    await ctx.send(f"You have bought {quantity} {item}(s) for {totalcostnice} {credits_name}.")
                else:
                    await self.config.member(ctx.author).inventory.set_raw(
                        item,
                        value={
                            "price": price,
                            "quantity": quantity,
                            "is_item": True,                        
                            "is_role": False,
                            "is_game": False,
                            "is_xmas": False,
                            "redeemable": True,
                            "redeemed": False,
                            "description": description,				
                            "giftable": False,
                            "gifted": False,                         
                        },
                    )
                    await ctx.send(
                        f"You have bought {quantity} {item}(s). You may now redeem it with `{ctx.clean_prefix}redeem {item}`"
                    )
        elif item in games:
            game_info = await self.config.guild(ctx.guild).games.get_raw(item)
            price = int(game_info.get("price"))
            pricenice = humanize_number(price) 
            quantityinstock = int(game_info.get("quantity"))
            credits_name = await bank.get_currency_name(ctx.guild)            
            redeemable = game_info.get("redeemable")
            if not redeemable:
                redeemable = False
            if quantityinstock == 0:
                return await ctx.send("Uh oh, this item is out of stock.")
            if quantity > 1:
                return await ctx.send("You can only buy one game.")
            if quantityinstock < quantity:
                return await ctx.send("Uh oh, there isn't enough in stock!")            
            if price <= balance:
                pass
            else:
                return await ctx.send(f"You don't have enough {credits_name}! This item costs {pricenice} {credits_name}")
            balance -= price
            quantityinstock -= quantity
            await bank.withdraw_credits(ctx.author, price)
            await self.config.guild(ctx.guild).games.set_raw(
                item, "quantity", value=quantityinstock
            )
            if not redeemable:
                await self.config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": quantity, 
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": True,
                        "is_xmas": False,
                        "redeemable": False,
                        "redeemed": True,
                        "giftable": False,
                        "gifted": False,                        
                    },
                )
                await ctx.send(f"You have bought {quantity} {item}(s) for {pricenice} {credits_name}.")
            else:
                await self.config.member(ctx.author).inventory.set_raw(
                    item,
                    value={
                        "price": price,
                        "quantity": quantity,                         
                        "is_item": False,                        
                        "is_role": False,
                        "is_game": True,
                        "is_xmas": False,
                        "redeemable": True,
                        "redeemed": False,
                        "giftable": False,
                        "gifted": False,                        
                    },
                )
                await ctx.send(
                    f"You have bought {quantity} {item}(s). You may now redeem it with `{ctx.clean_prefix}redeem {item}`"
                )
        elif item in xmas:
            xmasshop = await self.config.guild(ctx.guild).xmasshop()
            if not xmasshop:
                return await ctx.send("The Christmas shop is closed. Come back later!")            
            xmas_info = await self.config.guild(ctx.guild).xmas.get_raw(item)
            price = int(xmas_info.get("price"))
            totalcost = price * quantity
            totalcostnice = humanize_number(totalcost)
            quantityinstock = int(xmas_info.get("quantity"))
            credits_name = await bank.get_currency_name(ctx.guild)
            size = xmas_info.get("size")
            redeemable = xmas_info.get("redeemable")
            if not redeemable:
                redeemable = False
            if quantityinstock == 0:
                return await ctx.send("Uh oh, this item is out of stock.")
            if quantityinstock < quantity:
                return await ctx.send("Uh oh, there isn't enough in stock!")            
            if totalcost <= balance:
                pass
            else:
                return await ctx.send(f"You don't have enough {credits_name}! You need {totalcostnice} {credits_name} to buy {quantity} {item}(s)")
            try:
                info = await self.config.member(ctx.author).inventory.get_raw(item)
                author_quantity = int(info.get("quantity"))                
                balance -= price * quantity
                quantityinstock -= quantity
                await bank.withdraw_credits(ctx.author, totalcost)
                await self.config.guild(ctx.guild).xmas.set_raw(
                    item, "quantity", value=quantityinstock
                )
                if not redeemable:
                    author_quantity += quantity
                    await self.config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)               
                    await ctx.send(f"You have bought {quantity} {item}(s) for {totalcostnice} {credits_name}.")
                else:
                    author_quantity += quantity
                    await self.config.member(ctx.author).inventory.set_raw(item, "quantity", value=author_quantity)                                
                    await ctx.send(
                        f"You have bought {quantity} {item}(s). You may now redeem it with `{ctx.clean_prefix}redeem {item}`"
                    )
            except KeyError:
                balance -= price * quantity
                quantityinstock -= quantity
                await bank.withdraw_credits(ctx.author, totalcost)
                await self.config.guild(ctx.guild).xmas.set_raw(
                    item, "quantity", value=quantityinstock
                )
                if not redeemable:
                    await self.config.member(ctx.author).inventory.set_raw(
                        item,
                        value={
                            "price": price,
                            "quantity": quantity,      
                            "is_item": False,                        
                            "is_role": False,
                            "is_game": False,
                            "is_xmas": True,
                            "redeemable": False,
                            "redeemed": True,
                            "giftable": True,
                            "gifted": False,
                            "size": size,
                        },
                    )
                    await ctx.send(f"You have bought {quantity} {item}(s) for {totalcostnice} {credits_name}.")
                else:
                    await self.config.member(ctx.author).inventory.set_raw(
                        item,
                        value={
                            "price": price,
                            "quantity": quantity,      
                            "is_item": False,                        
                            "is_role": False,
                            "is_game": False,
                            "is_xmas": True,
                            "redeemable": True,
                            "redeemed": False,
                            "giftable": True,
                            "gifted": False,
                            "size": size,				
                        },
                    )
                    await ctx.send(
                        f"You have bought {quantity} {item}(s). You may now redeem it with `{ctx.clean_prefix}redeem {item}`"
                    )
        else:
            await ctx.send(":x: This item doesn't exist in any of the shops. Try again:")
            page = "roles"
            await self._show_store(ctx, page)

    @commands.command(name="return", aliases=["sell", "refund"])
    @commands.guild_only()
    async def store_return(self, ctx: commands.Context, quantity: Optional[int] = 1, *, item: str = ""):          
        """Return an item, you will only receive 10% of the price you paid."""
        enabled = await self.config.guild(ctx.guild).enabled()
        credits_name = await bank.get_currency_name(ctx.guild)
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")
        balance = int(
            await bank.get_balance(ctx.author)
        )
        inventory = await self.config.member(ctx.author).inventory.get_raw()
        item_all = "all"
        item = item.lower()
        if item in inventory:
            pass
        elif item == item_all:
            pass
        else:
            return await ctx.send("You don't own this item.")
        if item == item_all:
            total_price = 0
            for i in inventory:
                info = await self.config.member(ctx.author).inventory.get_raw(i)
                is_fish = info.get("is_fish")
                if is_fish:
                    price = int(info.get("price"))
                    inv_quantity = info.get("quantity")
                    if inv_quantity == 1:
                        await self.config.member(ctx.author).inventory.clear_raw(i)
                        total_price += price
                    if inv_quantity > 1:
                        await self.config.member(ctx.author).inventory.clear_raw(i)
                        quantity_price = inv_quantity * price
                        total_price += quantity_price
            return_price = humanize_number(total_price)
            await bank.deposit_credits(ctx.author, total_price) 
            return await ctx.send(
                f"You have received {return_price} {credits_name}."
            )    
        info = await self.config.member(ctx.author).inventory.get_raw(item)
        redeemed = info.get("redeemed")
        if redeemed:
            return await ctx.send("You cannot return an item you have redeemed.")
        inv_quantity = info.get("quantity")
        is_item = info.get("is_item")
        if is_item:
            if quantity > inv_quantity:
                return await ctx.send(f"You don't have that many {item}(s).")
            items = await self.config.guild(ctx.guild).items.get_raw(item)
            quantityinstock = int(items.get("quantity"))
            quantityinstock += quantity 
            await self.config.guild(ctx.guild).items.set_raw(
                item, "quantity", value=quantityinstock
            )
            inv_quantity -= quantity
            if inv_quantity == 0:
                redeemed = info.get("redeemed")
                price = int(info.get("price"))
                return_priceint = int(round(price * 0.1)) * quantity
                return_price = humanize_number(return_priceint)
                balance += return_priceint      
                await self.config.member(ctx.author).inventory.clear_raw(item)
                await bank.deposit_credits(ctx.author, return_priceint)
                return await ctx.send(
                    f"You have returned {item} and got {return_price} {credits_name} back."
                )                
            else:
                await self.config.member(ctx.author).inventory.set_raw(
                    item, "quantity", value=inv_quantity
                )
                price = int(info.get("price"))
                return_priceint = int(round(price * 0.1)) * quantity
                return_price = humanize_number(return_priceint)
                balance += return_priceint    
                await bank.deposit_credits(ctx.author, return_priceint)                
                return await ctx.send(
                    f"You have returned {item} and got {return_price} {credits_name} back."
                )
                  
        is_game = info.get("is_game")
        if is_game:
            return await ctx.send("Games are not returnable.")
        is_xmas = info.get("is_xmas")
        if is_xmas:
            return await ctx.send("Christmas Gift's are not returnable.")
        is_role = info.get("is_role")
        if is_role:
            info = await self.config.guild(ctx.guild).roles.get_raw(item)
            role_name = info.get("role_name")
            role_obj = get(ctx.guild.roles, name=role_name)
            if role_obj:
                if quantity > 1:
                    return await ctx.send("You only have one of these to give back!")                   
                role = await self.config.guild(ctx.guild).roles.get_raw(item)
                quantityinstock = int(role.get("quantity"))
                quantityinstock += 1
                await self.config.guild(ctx.guild).roles.set_raw(
                    item, "quantity", value=quantityinstock
                )
                await ctx.author.remove_roles(role_obj)                
                redeemed = info.get("redeemed")
                price = int(info.get("price"))
                return_priceint = int(round(price * 0.1)) * quantity
                return_price = humanize_number(return_priceint)
                balance += return_priceint      
                await self.config.member(ctx.author).inventory.clear_raw(item)
                await bank.deposit_credits(ctx.author, return_priceint)
                return await ctx.send(
                    f"You have returned {item} and got {return_price} {credits_name} back."
                )
        is_fish = info.get("is_fish")
        if is_fish:
            inv_quantity = info.get("quantity")
            if quantity > inv_quantity:
                return await ctx.send(f"You don't have that many to sell! Leave quantity blank to sell all of them")
            if quantity == 1:
                price = int(info.get("price"))
                return_priceint = int(price * inv_quantity)
                return_price = humanize_number(return_priceint)
                balance += return_priceint      
                await self.config.member(ctx.author).inventory.clear_raw(item)
                await bank.deposit_credits(ctx.author, return_priceint)
                return await ctx.send(
                    f"You have received {return_price} {credits_name}."
                )
            one = 1
            if one < quantity < inv_quantity:
                price = int(info.get("price"))
                return_priceint = int(price * quantity)
                return_price = humanize_number(return_priceint)
                balance += return_priceint
                inv_quantity -= quantity
                await self.config.member(ctx.author).inventory.set_raw(
                    item, "quantity", value=inv_quantity
                )                
                await bank.deposit_credits(ctx.author, return_priceint) 
                return await ctx.send(
                    f"You have received {return_price} {credits_name}."
                )
            if quantity == inv_quantity:
                price = int(info.get("price"))
                return_priceint = int(price * quantity)
                return_price = humanize_number(return_priceint)
                balance += return_priceint
                await self.config.member(ctx.author).inventory.clear_raw(item)            
                await bank.deposit_credits(ctx.author, return_priceint) 
                return await ctx.send(
                    f"You have received {return_price} {credits_name}."
                )                                         

    @commands.command(aliases=["inv", "backpack"])
    @commands.guild_only()
    async def inventory(self, ctx: commands.Context):
        """See all items you own."""
        balance = int(await bank.get_balance(ctx.author))
        credits_name = await bank.get_currency_name(ctx.guild)
        inventory = await self.config.member(ctx.author).inventory.get_raw()
        lst = []
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)
            is_role = info.get("is_role")
            if is_role:
                quantity = info.get("quantity")
                cat = "Role"
                table = [cat, i, quantity]
                lst.append(table)
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)                
            is_xmas = info.get("is_xmas")
            if is_xmas:
                quantity = info.get("quantity")
                cat = "Xmas"
                table = [cat, i, quantity]
                lst.append(table)
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)                
            is_item = info.get("is_item")
            if is_item:
                quantity = info.get("quantity")
                cat = "Item"
                table = [cat, i, quantity]
                lst.append(table)
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)                
            is_game = info.get("is_game") 
            if is_game:           
                quantity = info.get("quantity")
                cat = "Game"
                table = [cat, i, quantity]
                lst.append(table)              
        if lst == []:
            output = "Nothing to see here, go buy something at the `!shop`"
        else:
            headers = ("Type", "Item", "Qty") 
            output = box(tabulate(lst, headers=headers), lang="md")
        embed = discord.Embed(
            colour=await ctx.embed_colour(),
            description=f"{output}",
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/752524729470025788/776788124755034112/backpack.png")
        embed.set_author(
            name=f"{ctx.author.display_name}'s inventory", icon_url=ctx.author.avatar_url,
        )            
        embed.set_footer(text="Inventory™")
        await ctx.send(embed=embed) 
        
    @commands.command()
    @commands.guild_only()
    async def gift(self, ctx: commands.Context, user: discord.Member, quantity: Optional[int] = 1, *, item: str = ""):
        """
	Gift another user a Christmas Present|Card!
	
        Example
        -----------
        `!gift @ThalamusZen 2 stocking filler`
        """
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")
        date = datetime.now()
        over_xmas = datetime(2021, 1, 1)
        if date > over_xmas:
            return await ctx.send("Christmas is over, see you again next year!")   
        xmasshop = await self.config.guild(ctx.guild).xmasshop()
        if not xmasshop:
            return await ctx.send("The Chistmas event is over!")        
        if quantity < 1:
            return await ctx.send("Think you're smart huh?")
        if user == ctx.author:
            return await ctx.send("Maybe you should send this to a friend instead...")
        if user == ctx.bot.user:
            return await ctx.send("No thank you, why don't you give it to Zen instead?")
        author_inv = await self.config.member(ctx.author).inventory.get_raw()
        item = item.lower()
        if item in author_inv:
            pass
        else:
            await ctx.send(":x: You don't own this item. Check your inventory below:")
            return await self.inventory(ctx)
        info = await self.config.member(ctx.author).inventory.get_raw(item)
        size = info.get("size")	
        giftable = info.get("giftable")
        if not giftable:
            return await ctx.send("You are not able to gift this item.")
        gifted = info.get("gifted")
        if gifted:
            return await ctx.send("You cannot gift an item that was gifted to you... rude.")
        author_quantity = int(info.get("quantity"))
        author_price = int(info.get("price"))
        if author_quantity < quantity:
            return await ctx.send(f"You don't have that many {item}(s) to give.")
        author_quantity -= quantity
        if author_quantity == 0:
            await self.config.member(ctx.author).inventory.clear_raw(item)
        else:            
            await self.config.member(ctx.author).inventory.set_raw(
                item, "quantity", value=author_quantity
            )
        giftee_inv = await self.config.member(user).inventory.get_raw()
        from_text = " from "
        authorname = (str(ctx.author.name))
        author_name = authorname.lower()
        iu = []
        iu.append(item)
        iu.append(from_text)
        iu.append(author_name)
        item_user = ''.join(iu)
        if item_user in giftee_inv:
            info = await self.config.member(user).inventory.get_raw(item_user)
            giftee_quantity = info.get("quantity")
            giftee_quantity += quantity
            await self.config.member(user).inventory.set_raw(
                item_user, "quantity", value=giftee_quantity
            )
        else:
            gifter = ctx.author.id
            await self.config.member(user).inventory.set_raw(
                item_user,
                    value={
                        "price": author_price,
                        "quantity": quantity,
                        "is_item": False,                         
                        "is_role": False,
                        "is_game": False,
                        "is_xmas": True,
                        "redeemable": False,
                        "redeemed": True,
                        "giftable": False,
                        "gifted": True,
			"size": size,
                        "gifter": gifter,
                    },
                )
        await ctx.send(
            f"You have gifted {quantity} {item}(s) to {user.name}."
        )      
        
    @commands.command()
    @commands.guild_only()
    async def open(self, ctx: commands.Context, *, item: str = ""):
        """Open a Christmas Present given to you by another user!
        
        Examples
        --------
        `!open christmas present from thalamus zen`
        """
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop module is disabled. Come back later!")
        date = datetime.now()
        xmas_date = datetime(2020, 12, 24)
        over_xmas = datetime(2021, 1, 1)
        if date < xmas_date:
            return await ctx.send("It's not Christmas yet! Wait until after the 24th of December.")
        if date > over_xmas:
            return await ctx.send("Christmas is over, see you again next year!")        
        author_inv = await self.config.member(ctx.author).inventory.get_raw()
        item = item.lower()
        if item in author_inv:
            pass
        else:
            await ctx.send(":x: You don't own this item. Check your inventory below:")		
            return await self.inventory(ctx)
        info = await self.config.member(ctx.author).inventory.get_raw(item)        
        giftable = info.get("giftable")
        if giftable:
            return await ctx.send("Consider gifting this present to someone using the `!gift` command")        
        gifted = info.get("gifted")
        if not gifted:
            return await ctx.send("You cannot open a present that hasn't been gifted to you.") 	
        author_quantity = int(info.get("quantity"))        
        author_quantity -= 1   
        if author_quantity == 0:
            await self.config.member(ctx.author).inventory.clear_raw(item)
        else:            
            await self.config.member(ctx.author).inventory.set_raw(
                item, "quantity", value=author_quantity
            )
        gifter_id = info.get("gifter")
        gifter = get(ctx.guild.members, id=gifter_id)
        size = info.get("size")
        if size == 'card':
            opening_messages = [
                "*You slide your finger into the opening of the envelope and tear it open...*",
                "*You smile at the gesture and rip open the envelope...*",
                "*Excited to see the card inside, you pull open the lapel of the envelope...*",
                "*Excited to see the card inside, you tear open the envelope and pull the card out...*",
                "*Smiling, you carefully open the envelope and pull the card out...*",
                "*Excited to read what is written in the card, you lift up the flap of the envelope and pull the card out...*",
            ]
            bot_talking = await ctx.send(random.choice(opening_messages))
            await asyncio.sleep(4)
            card_messages = [
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nWarmest thoughts and best wishes for a wonderful Holiday and a Happy New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nTo a joyful present and a well remembered past. Best wishes for a Happy Holidays and a magnificent New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nWhatever is beautiful. Whatever is meaningful. Whatever brings you happiness. May it be yours these Holidays and throughout the coming year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nWishing you and your loved ones peace, health, happiness, and prosperity in the coming New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nBest wishes for the Holidays and for health and happiness throughout the coming year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nWith all best wishes for a healthy, happy, and peaceful New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nMay you have a peaceful Holiday season, and much joy and prosperity in the New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nBest wishes for a happy and prosperous New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nI hope your Holiday Season is fun and festive, and full of sparkles!\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nWishing you a joyous Holiday Season and a most prosperous and healthy New Year.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nMay this Holiday Season bring only happiness and joy to you and your loved ones.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nMay the closeness of friends and the comfort of home, renew your spirits this Holiday Season.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nLet the spirit of love gently fill our hearts and homes. In this loveliest of seasons may you find many reasons for happiness.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nMay this Christmas end the present year on a cheerful note and make way for a fresh and bright New Year. Have a very Merry Christmas and a Happy New Year!\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nMay your Christmas sparkle with moments of love, laughter and goodwill, And may the year ahead be full of contentment and joy.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nThat warm feeling isn’t just the Christmas spirit. I think you left the oven on.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nThis holiday season let us treasure what is truly important in all our lives, the reason for the season: Cookies.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nI might not believe in Santa, but I still believe in a good Christmas card!\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nAnother Christmas already? Seriously, what the Elf?\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nGood tidings to you and happy Christmas for today and all the Christmases to come.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nChristmas isn’t about what you receive – it’s about the love that you give.\nFrom {gifter.mention}",
                f"\nTo {ctx.author.mention},\nMerry Christmas!\nThere is nothing quite like Christmas – the celebration, the decoration, and the pure excitement. Follow your joy this holiday season and in the new year.\nFrom {gifter.mention}",
            ]
            return await bot_talking.edit(content=random.choice(card_messages))
        elif size == 'sf':
            await ctx.send(f"{ctx.author.mention} is opening your Stocking filler, {gifter.mention}")
            placing_messages = [
                "*You excitedly stick your hand into your stock and pick out a random gift to open...*",
                f"*You place the gift upon your lap and thank {gifter.mention} with a warm smile...*",
                "*After excitedly emptying the stocking in front of you, you pick out a present and place it in front of you...*",
                "*You Excitedly empty all the presents inside the stocking in front of you, you pick one out to unwrap...*",
                "*After excitedly emptying the stocking in front of you, you pick out a present and place it onto your lap...*",
                "*Once you have emptied your stocking in front of you, you excitedly pick one out to unwrap...*",
                f"*Pulling a gift out of your stocking, you look at {gifter.mention} with an excited smile...*",
                f"*Reaching into your stocking, you pull out a gift and place it onto your lap, looking at {gifter.mention} with a warm smile...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(5)
            opening_messages = [
                "*You are quick to rip the red and white wrapping paper from around the present...*",
                "*Excited to see what's inside, you quickly rip open the Christmas Tree printed wrapping paper...*",
                "*You delicately tear the wrapping paper from around the present...*",
                "*Excited to see what's inside, you quickly rip open the candy cane printed wrapping paper...*",
                f"*You look at {gifter.mention} with a warm smile and delicately begin to unwrap the present...*",
                "*With an excited smile, you look down at the present in front of you and tear open the wrapping paper...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(5)            
            sf_messages = [
                f"{ctx.author.mention} **|** You've received: **A £10 Steam gift card**",
                f"{ctx.author.mention} **|** You've received: **A pair of cute Gloves**",
                f"{ctx.author.mention} **|** You've received: **A mini Rubix cube**",
                f"{ctx.author.mention} **|** You've received: **A bag of assorted sweeties**",
                f"{ctx.author.mention} **|** You've received: **A tub of Nutella**",
                f"{ctx.author.mention} **|** You've received: **A pack of scented candles**",
                f"{ctx.author.mention} **|** You've received: **A pack of small wooden picture frames**",
                f"{ctx.author.mention} **|** You've received: **A set of Chibi Overwatch stickers**",
                f"{ctx.author.mention} **|** You've received: **A set of Whiskey stones**",
                f"{ctx.author.mention} **|** You've received: **A set of silk pyjamas**",
                f"{ctx.author.mention} **|** You've received: **Discord Nitro for the next... oh it's already expired**",
                f"{ctx.author.mention} **|** You've received: **400-in-1 Retro Handheld game**",
                f"{ctx.author.mention} **|** You've received: **DND/I'm Gaming Socks**",
                f"{ctx.author.mention} **|** You've received: **Bastion Funko Pop**",
                f"{ctx.author.mention} **|** You've received: **Torbjorn's Hammer Replica**",
                f"{ctx.author.mention} **|** You've received: **\"My Ultimate is Charging\" Overwatch themed Mug**",
                f"{ctx.author.mention} **|** You've received: **A personalised face cushion of {gifter.mention}**",
                f"{ctx.author.mention} **|** You've received: **A Smartphone projector**",
                f"{ctx.author.mention} **|** You've received: **Flamingo Slippers**",
                f"{ctx.author.mention} **|** You've received: **Infatable Jesus**",
                f"{ctx.author.mention} **|** You've received: **A Star Wars Origami set**",
                f"{ctx.author.mention} **|** You've received: **A Dual foot massager**",
                f"{ctx.author.mention} **|** You've received: **Unicorn poo bath bombs**",
                f"{ctx.author.mention} **|** You've received: **Personalised Chocolate Orange Christmas Pudding**",
                f"{ctx.author.mention} **|** You've received: **Handmade Soap Collection**",
                f"{ctx.author.mention} **|** You've received: **Personalised Christmas Santa Toblerone Bar**",
                f"{ctx.author.mention} **|** You've received: **A Cactus growing kit**",
                f"{ctx.author.mention} **|** You've received: **Marmite Popcorn**",
                f"{ctx.author.mention} **|** You've received: **Light Up Unicorn Slippers**",
                f"{ctx.author.mention} **|** You've received: **Millennium Falcon 3D Model Kit**",
                f"{ctx.author.mention} **|** You've received: **\"For Fox Sake\" Mug**",
                f"{ctx.author.mention} **|** You've received: **David Bowie Tea Towel**",
                f"{ctx.author.mention} **|** You've received: **Freddie Mercury Tea Towel**",
                f"{ctx.author.mention} **|** You've received: **52 Things to do while you poo book**",
            ] 
            return await bot_talking.edit(content=random.choice(sf_messages))            
        elif size == 'cp':
            await ctx.send(f"{ctx.author.mention} is opening your Christmas present, {gifter.mention}")
            placing_messages = [
                "*You excitedly place the gift upon your lap and smile...*",
                "*You slide out the present from beneath the Christmas tree...*",
                "*You excitedly slide out a present from under the tree and place it in front of you...*",
                "*After excitedly placing the present in front of you, you pick it up and place it onto your lap...*",
                "*You kneel in front of the Christmas tree and pick out a present to slide out and unwrap...*",
                f"*After pulling your present out from beneath the tree, you look at {gifter.mention} with an excited smile...*",
                f"*Reaching under the tree, you pull out a present and place it onto your lap, looking at {gifter.mention} with a warm smile...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(5)
            opening_messages = [
                "*Excited to see what's inside, you quickly rip open the Overwatch themed wrapping paper...*",
                "*Excited to see what's inside, you quickly rip open the Christmas Tree printed wrapping paper...*",
                "*Excited to see what's inside, you quickly rip open the candy cane printed wrapping paper...*",
                f"*You look at {gifter.mention} with a warm smile and delicately begin to unwrap the present...*",
                "*With an excited smile, you look down at the present in front of you and tear open the wrapping paper...*",
                "*You are quick to rip the red and white wrapping paper from the present...*",
                "*You delicately tear the wrapping paper from around the present...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(5)            
            cp_messages = [
                f"{ctx.author.mention} **|** You've received: **Overwatch 2**",                
                f"{ctx.author.mention} **|** You've received: **A red Among Us Plush doll**",
                f"{ctx.author.mention} **|** You've received: **A blue Among Us Plush doll**",
                f"{ctx.author.mention} **|** You've received: **A yellow Among Us Plush doll**",
                f"{ctx.author.mention} **|** You've received: **A pink Among Us Plush doll**",
                f"{ctx.author.mention} **|** You've received: **Bluetooth Headphones beanie**",
                f"{ctx.author.mention} **|** You've received: **Google Stadia Permiere Edition**",
                f"{ctx.author.mention} **|** You've received: **A custom Playstation/XBox controller**",
                f"{ctx.author.mention} **|** You've received: **A Pikachu onesie**",
                f"{ctx.author.mention} **|** You've received: **A Mancro Laptop Backpack**",
                f"{ctx.author.mention} **|** You've received: **Monopoly Gamer: Overwatch Edition**",
                f"{ctx.author.mention} **|** You've received: **Lego D.Va and Reinhardt**",
                f"{ctx.author.mention} **|** You've received: **The Art of Overwatch Book**",
                f"{ctx.author.mention} **|** You've received: **One Night Escape For Two With Dinner**",
                f"{ctx.author.mention} **|** You've received: **A pair of Blade Runner whiskey glasses**",
                f"{ctx.author.mention} **|** You've received: **Pierre the Penis pillow**",
                f"{ctx.author.mention} **|** You've received: **Pierre the Penis slippers**",
                f"{ctx.author.mention} **|** You've received: **Jumbo Pierre the Penis body pillow**",
                f"{ctx.author.mention} **|** You've received: **A fur Unicorn blanket**",
                f"{ctx.author.mention} **|** You've received: **The Foam Master 2000 coffee machine**",
                f"{ctx.author.mention} **|** You've received: **Apple AirPods Pro with Wireless Charging Case**",
                f"{ctx.author.mention} **|** You've received: **Cold brew iced coffee maker**",
                f"{ctx.author.mention} **|** You've received: **A black water resistant Bluetooth speaker**",
                f"{ctx.author.mention} **|** You've received: **A pair of Tartan Check Pyjamas in Medium**",
                f"{ctx.author.mention} **|** You've received: **Bean bag chair and stool set**",
                f"{ctx.author.mention} **|** You've received: **Party Popping Popcorn maker**",
                f"{ctx.author.mention} **|** You've received: **A vintage Popcorn maker**",
                f"{ctx.author.mention} **|** You've received: **LED Projector Alarm clock**",
                f"{ctx.author.mention} **|** You've received: **A pair of cream cross strap Faux Fur Slippers**",
                f"{ctx.author.mention} **|** You've received: **Hair Straighteners with Styling Set**",
                f"{ctx.author.mention} **|** You've received: **Lego Overwatch Hanzo vs Genji**",
                f"{ctx.author.mention} **|** You've received: **18-in-1 Ulitmate Multi Grooming Kit**",
                f"{ctx.author.mention} **|** You've received: **Maxi Micro Eco Deluxe Scooter**",
                f"{ctx.author.mention} **|** You've received: **Monopoly: Overwurst Edition**",
                f"{ctx.author.mention} **|** You've received: **Yoga Mat Towel in Vivid blue**",
                f"{ctx.author.mention} **|** You've received: **LED Projector Alarm clock**",
                f"{ctx.author.mention} **|** You've received: **Hitachi Magic Wand Massager**",
                f"{ctx.author.mention} **|** You've received: **STEELSERIES Apex Pro TKL Mechanical Gaming Keyboard**",
                f"{ctx.author.mention} **|** You've received: **RAZER Cynosa V2 Chroma Gaming Keyboard**",
                f"{ctx.author.mention} **|** You've received: **LOGITECH G502 Hero Optical Gaming Mouse**"
                f"{ctx.author.mention} **|** You've received: **RAZER Basilisk Ultimate Wireless Optical Gaming Mouse**"
                f"{ctx.author.mention} **|** You've received: **STEELSERIES Arctis 7 Wireless 7.1 Gaming Headset**"
                f"{ctx.author.mention} **|** You've received: **MSI Optix G241 Full HD 24\" IPS LCD Gaming Monitor - Black**"
            ] 
            return await bot_talking.edit(content=random.choice(cp_messages))
        elif size == 'ch': 
            await ctx.send(f"{ctx.author.mention} is opening your Christmas hamper, {gifter.mention}")
            placing_messages = [
                "*You excitedly place the hamper on the floor between your feet and smile...*",
                "*You slide out the hamper from beneath the Christmas tree...*",
                "*You excitedly slide out the hamper from under the tree and place it in front of you...*",
                "*After excitedly placing the hamper in front of you, you admire it's wrapping for a moment...*",
                "*You kneel in front of the Christmas tree and slide out your hamper...*",
                f"*After pulling your hamper out from beneath the tree, you look at {gifter.mention} with an excited smile...*",
                f"*Reaching under the tree, you pull out your hamper and place it between your feet, before looking at {gifter.mention} with a warm smile...*",                
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(5)
            opening_messages = [
                "*You are quick to tear away the long red ribbon from the basket and look inside...*",
                "*You delicately tear the ribbon from around the basket and look inside...*",
                "*Excited to see what's inside, you quickly pull away the pink ribbon from around the hamper...*",
                "*Excited to see what's inside, you quickly pull away the blue ribbon from around the hamper...*",
                "*Excited to see what's inside, you quickly pull away the red ribbon from around the hamper...*",
                "*Excited to see what's inside, you quickly pull away the white ribbon from around the hamper...*",
                f"*You look at {gifter.mention} with a warm smile and delicately begin to unwrap the hamper...*",
                "*With an excited smile, you look down at the hamper in front of you and pull away the ribbon before opening the lid...*",
                "*You are quick to flip open the lid of the hamper backet to see what is inside...*",               
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(5)            
            ch_messages = [
                f"{ctx.author.mention} **|** You've received: **The Ultimate Candy and Snacks Variety Christmas Hamper**",
                f"{ctx.author.mention} **|** You've received: **Continental Beer Basket** - The lucky recipient of this delightful beer gift won't wait long to crack open the pair of premium Continental lagers.",
                f"{ctx.author.mention} **|** You've received: **Italian Wine Chest** - Presented in a Vintage wooden chest is a selection of some of the finest wines from Italy.",
                f"{ctx.author.mention} **|** You've received: **Luxury Pamper Gift** - Something for the sweet tooth and something to soothe the skin all packed in one gorgeous gift basket.",
                f"{ctx.author.mention} **|** You've received: **The Super Deluxe Chocolate Bouquet** - Packed to bursting with family favourites and Cadbury classics, this might just be the best hamper of all.",
                f"{ctx.author.mention} **|** You've received: **Super Mega Mix Hamper** - An amazing mix of retro school sweets and chocolate bars",
                f"{ctx.author.mention} **|** You've received: **The Prosecco and Christmas Treats Hamper** - Presented inside a festive red box, inside you will find a scrumptious bottle of Prosecco a delicious pack of Joe and Sephs Mince Pie flavour popcorn and a box of luxury Belgian Chocolates.",
                f"{ctx.author.mention} **|** You've received: **The Continental Hamper** - The whitewash wicker basket also contains an award-winning Cider Chutney, Olive & Sesame Mini Breadsticks from Greece, Smoked Almonds, Fresh Ground Coffee and White Wine Vinegar of Kalamata.",
                f"{ctx.author.mention} **|** You've received: **The Great British Tower** - Sealed with a flourish of red, white & blue ribbon, this best of British tower contains a host of award-winning goodies including Thin & Crispy Oatcakes from Scotland and a mouth watering Cranberry & White Chocolate Fudge from Northern Ireland.",
                f"{ctx.author.mention} **|** You've received: **The Ultimate Celebration Hamper** - Indulge in a fine selection of chocolates including ones with interesting combinations of flavours such as sea salt, strawberry and Champagne and wash it down with a glass of Moet.",
                f"{ctx.author.mention} **|** You've received: **Proudly Vegan Hamper** - In this basket you'll find Indie Bay Cracked Pepper Crunchy Pretzels, Franks Chocolate Orange & Cranberry Oaties, Guppy's Chocolate Orange Shards, toffee apple and cinnamon gourmet popcorn and more.",
                f"{ctx.author.mention} **|** You've received: **British Honey Company Spirits Gift Hamper** - includes smoked honey bourbon, honey spiced rum and classic London dry gin with honey.",
                f"{ctx.author.mention} **|** You've received: **Baked Treats Box** - Filled with award winning ginger parkin cake, shortbread, biscuits and award winning treats.",
                f"{ctx.author.mention} **|** You've received: **Speciality Craft Beers Of The World** - Includes beers from craft breweries such as BrewDog, Leffe or Tiny Rebel.",
                f"{ctx.author.mention} **|** You've received: **British Letterbox Charcuterie** - A hamper of award winning, artisan British charcuterie, made in Dorset, containing 5 of The Real Cure's most popular cured meats.",
                f"{ctx.author.mention} **|** You've received: **World's Hottest Rare Chilli Collection** - Turn up the heat in your kitchen with these 6 Pots of 100% Pure Whole, Ground and Flakes of Chillies from around the world.",
                f"{ctx.author.mention} **|** You've received: **Cheese Lovers Letter Box Hamper** - Contains Godminster's award winning cheddar from the West Country and Caws Cryf from Wales - as well as biscuits for cheese, salted nuts and red onion chutney.",                
            ] 
            return await bot_talking.edit(content=random.choice(ch_messages))
        elif size == 'lp': 
            await ctx.send(f"{ctx.author.mention} is opening your Luxury Christmas present, {gifter.mention}")
            placing_messages = [
                "*You delicately place the gift upon your lap and smile...*",
                "*You slide out the present from beneath the Christmas tree...*",
                "*You excitedly slide out a present from under the tree and place it in front of you...*",
                "*After excitedly placing the present in front of you, you pick it up and place it onto your lap...*",
                "*You kneel in front of the Christmas tree and pick out a present to slide out and unwrap...*",
                f"*After pulling your present out from beneath the tree, you look at {gifter.mention} with an excited smile...*",
                f"*Reaching under the tree, you pull out a present and place it onto your lap, looking at {gifter.mention} with a warm smile...*",		    
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(5)
            opening_messages = [
                "*You delicately tear the silver and white wrapping paper from the present...*",
                "*You delicately tear the gold and white wrapping paper from around the present...*",
                "*Excited to see what's inside, you quickly rip away the expensive looking Overwatch themed wrapping paper...*",
                "*Excited to see what's inside, you quickly rip away the expensive looking Christmas Tree printed wrapping paper...*",
                "*Excited to see what's inside, you quickly rip away the expensive looking candy cane printed wrapping paper...*",
                f"*You look at {gifter.mention} with a warm smile and delicately begin to unwrap their present...*",
                "*With an excited smile, you look down at the present in front of you and tear open the wrapping paper...*",
                "*You are quick to rip the red and white wrapping paper from the present...*",
                "*You delicately tear the wrapping paper from around the present...*",		    
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(5)            
            lp_messages = [
                f"{ctx.author.mention} **|** You've received: **Acer Predator Thronos Gaming Cockpit**",
                f"{ctx.author.mention} **|** You've received: **X Rocker Pro Series Gaming Chair**",
                f"{ctx.author.mention} **|** You've received: **Nintendo Switch with Green and Blue Joy-Con - Animal Crossing: New Horizons Edition**",
                f"{ctx.author.mention} **|** You've received: **A custom made Arcade Machine coffee table**",
                f"{ctx.author.mention} **|** You've received: **Oculus Quest All-in-one VR Gaming Headset**",
                f"{ctx.author.mention} **|** You've received: **Samsung 49-Inch Curved Gaming Monitor**",
                f"{ctx.author.mention} **|** You've received: **SteelSeries Arctics Pro wireless gaming headset**",
                f"{ctx.author.mention} **|** You've received: **A Yellow Nintendo Switch Lite with SanDisk 256GB MicroSDXC Memory Card**",
                f"{ctx.author.mention} **|** You've received: **Razer Blade 15 Gaming laptop**",
                f"{ctx.author.mention} **|** You've received: **VanMoof Electrified X2 E-Bike**",
                f"{ctx.author.mention} **|** You've received: **Canon EOS R DLSR Camera**",
                f"{ctx.author.mention} **|** You've received: **Roomba 675 Robot Vacuum**",
                f"{ctx.author.mention} **|** You've received: **Oral-B GENIUS X Electric Toothbrush**",
                f"{ctx.author.mention} **|** You've received: **iPhone 12 Pro Max**",
                f"{ctx.author.mention} **|** You've received: **Portable Full HD LED Smart Home Theater Projector**",
                f"{ctx.author.mention} **|** You've received: **Kindle Paperwhite**",
                f"{ctx.author.mention} **|** You've received: **Fitbit Sense, Health and Fitness Watch with Heart Rate Monitor**",
                f"{ctx.author.mention} **|** You've received: **Samsung 49-Inch CRG9 QLED Curved Gaming Monitor**",
                f"{ctx.author.mention} **|** You've received: **Breville Barista Touch Espresso Maker**",
                f"{ctx.author.mention} **|** You've received: **Apple MacBook Pro (16-inch, 16GB RAM, 512GB Storage, 2.6GHz Intel Core i7) - Space Grey**",
            ] 
            return await bot_talking.edit(content=random.choice(lp_messages))
        elif size == 'gtx': 
            await ctx.send(f"{ctx.author.mention} is opening your Geforce RTX 3080, {gifter.mention}")
            placing_messages = [
                "*You slide out the present from beneath the Christmas tree...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(5)
            opening_messages = [
                "*You are quick to rip the bright pink and white wrapping paper from around the present...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(5)            
            gtx_messages = [
                f"{ctx.author.mention} **|** You've received: An MSI Geforce RTX 3080, 10GB of GDDR6X RAM, Gaming X Trio Ampere graphics card.",
            ] 
            return await bot_talking.edit(content=random.choice(gtx_messages))

    @commands.command()
    @commands.guild_only()
    async def show(self, ctx: commands.Context, *, item: str):
        """Show more information about an item in the shop."""
        item = item.strip("@")
        item = item.lower()
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()

        if item in items:
            info = await self.config.guild(ctx.guild).items.get_raw(item)
            item_type = "Item"
        elif item in roles:
            info = await self.config.guild(ctx.guild).roles.get_raw(item)
            item_type = "Role"
        elif item in games:
            info = await self.config.guild(ctx.guild).games.get_raw(item)
            item_type = "Game"
        elif item in xmas:
            info = await self.config.guild(ctx.guild).xmas.get_raw(item)
            item_type = "Xmas"            
        else:
            return await ctx.send("This item isn't buyable.")
        price = info.get("price")
        quantity = info.get("quantity")
        redeemable = info.get("redeemable")
        description = info.get("description")
        if not redeemable:
            redeemable = False
        embed = discord.Embed(
            title=f"{item}",
            colour=await ctx.embed_colour(),
            description=f"**Type:** {item_type}\n**Price:** {price}\n**Description:** {description}",
            timestamp=datetime.now(),
	)
        embed.set_footer(text="Information™")
        await ctx.send(embed=embed)

    @commands.command(aliases=["reminv", "drop"])
    @commands.guild_only()
    async def removeinventory(self, ctx: commands.Context, quantity: Optional[int] = 1, *, item: str):
        """Remove an item from your inventory."""
        inventory = await self.config.member(ctx.author).inventory.get_raw()
        item = item.lower()
        if item not in inventory:
            return await ctx.send("You don't own this item.")
        info = await self.config.member(ctx.author).inventory.get_raw(item)	
        inv_quantity = int(info.get("quantity"))
        if quantity <= 0:
            return await ctx.send("Uh oh, quantity has to be more than 0.")
        if quantity > inv_quantity:
            return await ctx.send("You don't have that many {item}(s).")
        inv_quantity -= quantity
        if inv_quantity == 0:
            await self.config.member(ctx.author).inventory.clear_raw(item)
        else:
            await self.config.member(ctx.author).inventory.set_raw(
                item, "quantity", value=inv_quantity
	    )
        await ctx.send(f"You've dropped {quantity} {item}(s) from your inventory.")

    @commands.command()
    @commands.guild_only()
    async def redeem(self, ctx: commands.Context, *, item: str):
        """Redeem an item from your inventory."""
        inventory = await self.config.member(ctx.author).inventory.get_raw()
        item = item.lower()
        if item not in inventory:
            return await ctx.send("You don't own this item.")
        info = await self.config.member(ctx.author).inventory.get_raw(item)
        is_role = info.get("is_role")
        if is_role:
            return await ctx.send("Roles aren't redeemable.")
        redeemable = info.get("redeemable")
        if not redeemable:
            return await ctx.send("This item isn't redeemable.")
        redeemed = info.get("redeemed")
        if redeemed:
            return await ctx.send("You have already redeemed this item.")
        ping_id = await self.config.guild(ctx.guild).ping()
        if not ping_id:
            return await ctx.send("Uh oh, if you see this, let Zen know.")
        ping = get(ctx.guild.members, id=ping_id)
        if not ping:
            ping = get(ctx.guild.roles, id=ping_id)
            if not ping:
                return await ctx.send("Uh oh, if you see this, let Zen know.")
            if not ping.mentionable:
                await ping.edit(mentionable=True)
                await ctx.send(
                    f"{ping.mention}, {ctx.author.mention} would like to redeem their {item}."
                )
                await ping.edit(mentionable=False)
            else:
                await ctx.send(
                    f"{ping.mention}, {ctx.author.mention} would like to redeem their {item}."
                )
            author_quantity = int(info.get("quantity"))
            author_quantity -= 1
            if author_quantity == 0:
                await self.config.member(ctx.author).inventory.clear_raw(item)
            else:
                await self.config.member(ctx.author).inventory.set_raw(
                    item, "quantity", value=author_quantity
                )
        else:
            await ctx.send(
                f"{ping.mention}, {ctx.author.mention} would like to redeem their {item}."
            )
            author_quantity = int(info.get("quantity"))
            author_quantity -= 1
            if author_quantity == 0:
                await self.config.member(ctx.author).inventory.clear_raw(item)
            else:
                await self.config.member(ctx.author).inventory.set_raw(
                    item, "quantity", value=author_quantity
                )

    async def _show_store(self, ctx, page):
        xmasshop = await self.config.guild(ctx.guild).xmasshop()
        page = page.lower()
        if page == "role":
            page_choice = 0
        elif page == "roles":
            page_choice = 0
        elif page == "item":
            page_choice = 1
        elif page == "items":
            page_choice = 1
        elif page == "xmas":
            xmasshop = await self.config.guild(ctx.guild).xmasshop()
            if not xmasshop:
                await ctx.send("The Christmas shop is closed. Take a look at the role shop instead")
                page_choice = 0
            else:
                page_choice = 2
        else:
            page_choice = 0
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()
        credits_name = await bank.get_currency_name(ctx.guild)
        embeds = []
        embed_r = discord.Embed(
           title="__**Role Shop**__",
           colour=await ctx.embed_colour(),
           timestamp=datetime.now(),
        )
        embed_r.set_thumbnail(url="https://cdn.discordapp.com/attachments/768197304158257234/792421750733537310/Shop.png")	
        embed_r.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_r.set_footer(text=f"Shoppy™ • Use the arrows below to change shops")
        embed_i = discord.Embed(
           title="__**Item Shop**__",		
           colour=await ctx.embed_colour(),
           timestamp=datetime.now(),            
        )
        embed_i.set_thumbnail(url="https://cdn.discordapp.com/attachments/768197304158257234/792421750733537310/Shop.png")
        embed_i.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_i.set_footer(text=f"Shoppy™ • Use the arrows below to change shops")
        embed_g = discord.Embed(
           title="__**Game Shop**__",		
           colour=await ctx.embed_colour(),
           timestamp=datetime.now(),            
        )
        embed_g.set_thumbnail(url="https://cdn.discordapp.com/attachments/768197304158257234/792421750733537310/Shop.png")
        embed_g.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_g.set_footer(text=f"Shoppy™ • Use the arrows below to change shops")
        if not xmasshop:
            pass
        else:
            embed_x = discord.Embed(
                title="__**Christmas Shop**__",		
                colour=await ctx.embed_colour(),
                timestamp=datetime.now(),            
            )            
            embed_x.set_thumbnail(url="https://cdn.discordapp.com/attachments/768197304158257234/792421750733537310/Shop.png")	
            embed_x.set_author(
                name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
            )
            embed_x.set_footer(text=f"Shoppy™ • Use the arrows below to change shops")
            xmas_embed = []
            sorted_xmas = []
        role_embed = []
        item_embed = []
        game_embed = []
        sorted_role = []
        sorted_item = []
        sorted_game = []
        for r in roles:
            role = await self.config.guild(ctx.guild).roles.get_raw(r)
            priceint = int(role.get("price"))
            price = humanize_number(priceint)
            quantity = int(role.get("quantity"))
            role_name = role.get("role_name")
            table = [r, priceint, quantity, role_name]
            role_embed.append(table)
            sorted_role = sorted(role_embed, key=itemgetter(1), reverse=True)
        for i in items:
            item = await self.config.guild(ctx.guild).items.get_raw(i)
            priceint = int(item.get("price"))
            price = humanize_number(priceint)
            quantity = int(item.get("quantity"))
            table = [i, priceint, quantity]		
            item_embed.append(table)
            sorted_item = sorted(item_embed, key=itemgetter(1), reverse=True)		
        for g in games:
            game = await self.config.guild(ctx.guild).games.get_raw(g)
            priceint = int(game.get("price"))
            price = humanize_number(priceint)
            quantity = int(game.get("quantity"))
            table = [g, priceint, quantity]		
            game_embed.append(table)
            sorted_game = sorted(game_embed, key=itemgetter(1), reverse=True)
        if not xmasshop:
            pass
        else:            
            for x in xmas:
                xmas = await self.config.guild(ctx.guild).xmas.get_raw(x)
                priceint = int(xmas.get("price"))
                price = humanize_number(priceint)
                quantity = int(xmas.get("quantity"))
                table = ["\ud83c\udf81", x, priceint, quantity]
                xmas_embed.append(table)
                sorted_xmas = sorted(xmas_embed, key=itemgetter(2), reverse=True)
        if sorted_role == []:
            embed_r.description="Nothing to see here."
        else:
            headers = ("Item", "Price", "Qty", "Looks like")
            output = box(tabulate(sorted_role, headers=headers, colalign=("left", "right", "right",)), lang="md")		
            embed_r.description=f"Welcome to Elune's Role shop!\n\nAfter purchasing your role, it will automatically be applied to you.\nIf you wish remove a role from yourself, use the `!return` command and in doing so, you will recieve a 10% refund.\n\n`!buy <quantity> <item_name>`\n{output}"
            embeds.append(embed_r)	
        if sorted_item == []:
            embed_i.description="Nothing to see here."
        else:
            headers = ("Item", "Price", "Qty")
            output = box(tabulate(sorted_item, headers=headers, colalign=("left", "right", "right",)), lang="md")		
            embed_i.description=f"Welcome to Elune's Item shop!\n\nThe below items can be redeemed with the `!redeem` command.\nItems can be returned using the `!return` command, as long as they haven't been redeemed.\nTo see more info on an item, use the `!show` command.\n\n`!buy <quantity> <item_name>`\n{output}"
            embeds.append(embed_i)
        if sorted_game == []:
            embed_g.description="Nothing to see here."
        else:
            headers = ("Item", "Price", "Qty")
            output = box(tabulate(sorted_game, headers=headers, colalign=("left", "right", "right",)), lang="md")		
            embed_g.description=f"Welcome to Elune's Game shop, here you will find gifts to send your friends during the festive period!\nAfter purchasing your gift, use the `!gift` command to send them to your friends.\n\n`!buy <quantity> <item_name>`\n{output}"
            embeds.append(embed_g)
        if not xmasshop:
            pass
        else:            
            if sorted_xmas == []:
                embed_x.description="Nothing to see here."
            else:
                headers = ("", "Item", "Price", "Qty")
                output = box(tabulate(sorted_xmas, headers=headers, colalign=("left", "left", "right", "right",)), lang="md")		
                embed_x.description=f"Welcome to Elune's Christmas shop, here you will find gifts to send to your friends for the festive period!\n\nAfter your purchase, use the `!gift` command to gift the item to a friend.\nAfter the **24th of December** you will be able to open gifted presents using the `!open` command.\nChristmas items **cannot** be refunded using the `!return` command.\n\n`!buy <quantity> <item_name>`\n{output}"	
                embeds.append(embed_x)
        if embeds == []:
            embed_closed = discord.Embed(
               title="__**All shops are closed**__",
               colour=await ctx.embed_colour(),
               timestamp=datetime.now(),
            )
            embed_closed.set_thumbnail(url="https://cdn.discordapp.com/attachments/768197304158257234/792421750733537310/Shop.png")	
            embed_closed.set_author(
               name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
            )
            embed_closed.description="Come back soon!"	
            embed_closed.set_footer(text="Shoppy™")
            embeds.append(embed_closed)
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=page_choice, timeout=120)
