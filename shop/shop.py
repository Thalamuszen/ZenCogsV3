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
            enabled=False, items={}, roles={}, games={}, xmas={}, ping=None
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
    async def shop(self, ctx: commands.Context):
        """Display the shop."""
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")
        await self._show_store(ctx)

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

        item = item.lower()
        item = item.strip("@")
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
            await self._show_store(ctx)

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

    @commands.command()
    @commands.guild_only()
    async def inventory(self, ctx: commands.Context):
        """See all items you own."""
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
        """Gift another user a Christmas Present\Card!
        
        Examples
        --------
        `!gift @ThalamusZen 2 stocking filler`
        """
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")        
        if quantity < 1:
            return await ctx.send("Think you're smart huh?")
        if user == ctx.author:
            return await ctx.send("Maybe you should send this to a friend instead...")
        if user == ctx.bot.user:
            return await ctx.send("No thank you, why don't you give it to Zen instead?")
        author_inv = await self.config.member(ctx.author).inventory.get_raw()
        if item in author_inv:
            pass
        else:
            await ctx.send(":x: You don't own this item. Items are case sensitive. Check your inventory below:")
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
    async def open(self, ctx: commands.Context, *, item: str):
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
        if item in author_inv:
            pass
        else:
            await ctx.send(":x: You don't own this item. Items are case sensitive. Check your inventory below:")		
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
                "*You slide your finger into the crease of the envelope and tear it open...*",
                "*You *",
            ]
            bot_talking = await ctx.send(random.choice(opening_messages))
            await asyncio.sleep(3)
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
        if size == 'sf':
            await ctx.send(f"{ctx.author.mention} is opening your Stocking filler, {gifter.mention}")
            placing_messages = [
                "*You excitedly take the gift out of your stoking and smile...*",
                "*You ...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(3)
            opening_messages = [
                "*You are quick to rip the red and white wrapping paper from the present...*",
                "*You delicately tear the wrapping paper from around the present...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(3)            
            sf_messages = [
                f"{ctx.author.mention} You received: Overwatch 2",
                f"{ctx.author.mention} You received: A £10 Steam gift card",
            ] 
            return await bot_talking.edit(content=random.choice(sf_messages))            
        if size == 'cp':
            await ctx.send(f"{ctx.author.mention} is opening your Christmas present, {gifter.mention}")
            placing_messages = [
                "*You excitedly place the gift upon your lap and smile...*",
                "*You slide out the present from beneath the Christmas tree...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(3)
            opening_messages = [
                "*You are quick to rip the red and white wrapping paper from the present...*",
                "*You delicately tear the wrapping paper from around the present...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(3)            
            cp_messages = [
                f"{ctx.author.mention} You received: Overwatch 2",
                f"{ctx.author.mention} You received: A £10 Steam gift card",
            ] 
            return await bot_talking.edit(content=random.choice(cp_messages))
        if size == 'ch': 
            await ctx.send(f"{ctx.author.mention} is opening your Christmas hamper, {gifter.mention}")
            placing_messages = [
                "*You excitedly place the gift on the floor between your feet and smile...*",
                "*You slide out the present from beneath the Christmas tree...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(3)
            opening_messages = [
                "*You are quick to rip the red and white wrapping paper from the present...*",
                "*You delicately tear the wrapping paper from around the present...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(3)            
            ch_messages = [
                f"{ctx.author.mention} You received: Overwatch 2",
                f"{ctx.author.mention} You received: A £10 Steam gift card",
            ] 
            return await bot_talking.edit(content=random.choice(ch_messages))
        if size == 'lp': 
            await ctx.send(f"{ctx.author.mention} is opening your Luxury Christmas present, {gifter.mention}")
            placing_messages = [
                "*You excitedly place the gift upon your lap and smile...*",
                "*You slide out the present from beneath the Christmas tree...*",
            ]
            bot_talking = await ctx.send(random.choice(placing_messages))
            await asyncio.sleep(3)
            opening_messages = [
                "*You are quick to rip the red and white wrapping paper from the present...*",
                "*You delicately tear the wrapping paper from around the present...*",
            ]
            await bot_talking.edit(content=random.choice(opening_messages))
            await asyncio.sleep(3)            
            lp_messages = [
                f"{ctx.author.mention} You received: Overwatch 2",
                f"{ctx.author.mention} You received: A £10 Steam gift card",
            ] 
            return await bot_talking.edit(content=random.choice(lp_messages))            

    @commands.command()
    @commands.guild_only()
    async def show(self, ctx: commands.Context, *, item: str):
        """Show more information about an item in the shop."""
        item = item.strip("@")
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

    async def _show_store(self, ctx):
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
        embed_r.set_thumbnail(url=" https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png")	
        embed_r.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_r.set_footer(text="Shoppy™ - Use the arrows below to change shops")
        embed_i = discord.Embed(
           title="__**Item Shop**__",		
           colour=await ctx.embed_colour(),
           timestamp=datetime.now(),
        )
        embed_i.set_thumbnail(url=" https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png")
        embed_i.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_i.set_footer(text="Shoppy™ - Use the arrows below to change shops")
        embed_g = discord.Embed(
           title="__**Game Shop**__",		
           colour=await ctx.embed_colour(),
           timestamp=datetime.now(),
        )
        embed_g.set_thumbnail(url=" https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png")
        embed_g.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_g.set_footer(text="Shoppy™ - Use the arrows below to change shops")
        embed_x = discord.Embed(
           title="__**Christmas Shop**__",		
           colour=await ctx.embed_colour(),
           timestamp=datetime.now(),
        )
        embed_x.set_thumbnail(url=" https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png")	
        embed_x.set_author(
           name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
        )
        embed_x.set_footer(text="Shoppy™ - Use the arrows below to change shops")	
        role_embed = []
        item_embed = []
        game_embed = []
        xmas_embed = []
        sorted_role = []
        sorted_item = []
        sorted_game = []
        sorted_xmas = []
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
            embed_r.description=f"Welcome to Elune's Role shop!\n\nAfter purchasing your role, it will automatically be applied to you.\nIf you wish remove a role from yourself, use the `!return` command and in doing so, you will recieve a 10% refund.\n\n`!buy <quantity> <item_name>` - Item names are case sensitive.\n{output}"
            embeds.append(embed_r)	
        if sorted_item == []:
            embed_i.description="Nothing to see here."
        else:
            headers = ("Item", "Price", "Qty")
            output = box(tabulate(sorted_item, headers=headers, colalign=("left", "right", "right",)), lang="md")		
            embed_i.description=f"Welcome to Elune's Item shop!\n\nThe below items can be redeemed with the `!redeem` command.\nItems can be returned using the `!return` command, as long as they haven't been redeemed.\nTo see more info on an item, use the `!show` command.\n\n`!buy <quantity> <item_name>` - Item names are case sensitive.\n{output}"
            embeds.append(embed_i)
        if sorted_game == []:
            embed_g.description="Nothing to see here."
        else:
            headers = ("Item", "Price", "Qty")
            output = box(tabulate(sorted_game, headers=headers, colalign=("left", "right", "right",)), lang="md")		
            embed_g.description=f"Welcome to Elune's Game shop, here you will find gifts to send your friends during the festive period!\nWhen using `!buy` command, keep in mind that items are **case sensitive**.\nAfter purchasing your gift, use the `!gift` command to send them to your friends.\n\n`!buy <quantity> <item_name>` - Item names are case sensitive.\n{output}"
            embeds.append(embed_g)
        if sorted_xmas == []:
            embed_x.description="Nothing to see here."
        else:
            headers = ("", "Item", "Price", "Qty")
            output = box(tabulate(sorted_xmas, headers=headers, colalign=("left", "left", "right", "right",)), lang="md")		
            embed_x.description=f"Welcome to Elune's Christmas shop, here you will find gifts to send to your friends for the festive period!\n\nAfter your purchase, use the `!gift` command to gift the item to a friend.\nAfter the **24th of December** you will be able to open gifted presents using the `!open` command.\nChristmas items **cannot** be refunded using the `!return` command.\n\n`!buy <quantity> <item_name>` - Item names are case sensitive.\n{output}"	
            embeds.append(embed_x)
        if embeds == []:
            embed_closed = discord.Embed(
               title="__**All shops are closed**__",
               colour=await ctx.embed_colour(),
               timestamp=datetime.now(),
            )
            embed_closed.set_thumbnail(url=" https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png")	
            embed_closed.set_author(
               name=f"Silvermoon Bazaar", icon_url="https://cdn.discordapp.com/avatars/751844552670969866/9f035363fa69e094c61c9a33e24d4382.png",
            )
            embed_closed.description="Come back soon!"	
            embed_closed.set_footer(text="Shoppy™")
            embeds.append(embed_closed)
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, message=None, page=0, timeout=120)
