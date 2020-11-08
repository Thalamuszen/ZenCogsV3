import asyncio
import discord

from typing import Union
from discord.utils import get
from datetime import datetime

from redbot.core import Config, checks, commands, bank
from redbot.core.utils.chat_formatting import pagify, humanize_list, humanize_number
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
                await self.config.guild(ctx.guild).items.set_raw(
                    item_name,
                    value={
                        "price": price,
                        "quantity": quantity,
                        "redeemable": redeemable,
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
                await ctx.send("What is the size of the gift? small medium or large")
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
        if not redeemable:
            redeemable = False
        await ctx.send(
            f"**__{item}:__**\n*Type:* {item_type}\n*Price:* {price}\n*Quantity:* {quantity}\n*Redeemable:* {redeemable}"
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
        page_list = await self._show_store(ctx)
        if len(page_list) > 1:
            await menu(ctx, page_list, DEFAULT_CONTROLS)
        else:
            await ctx.send(embed=page_list[0])

    @commands.command()
    @commands.guild_only()
    async def buy(self, ctx: commands.Context, quantity: int, *, item: str = ""):      
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
        
        if not item:
            page_list = await self._show_store(ctx)
            if len(page_list) > 1:
                return await menu(ctx, page_list, DEFAULT_CONTROLS)
            return await ctx.send(embed=page_list[0])
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
                        "redeemed": True,
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
            page_list = await self._show_store(ctx)
            if len(page_list) > 1:
                return await menu(ctx, page_list, DEFAULT_CONTROLS)
            return await ctx.send(embed=page_list[0])

    @commands.command(name="return")
    @commands.guild_only()
    async def store_return(self, ctx: commands.Context, quantity: int, *, item: str = ""):          
        """Return an item, you will only receive 10% of the price you paid."""
        enabled = await self.config.guild(ctx.guild).enabled()
        credits_name = await bank.get_currency_name(ctx.guild)
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")
        balance = int(
            await bank.get_balance(ctx.author)
        )
        inventory = await self.config.member(ctx.author).inventory.get_raw()

        if item in inventory:
            pass
        else:
            return await ctx.send("You don't own this item.")
        info = await self.config.member(ctx.author).inventory.get_raw(item)
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
                await ctx.send(
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
                await ctx.send(
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
                await ctx.send(
                    f"You have returned {item} and got {return_price} {credits_name} back."
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
                role_text = f"__Role:__ **{i}** | Quantity: {quantity}"
                lst.append(role_text)
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)                
            is_xmas = info.get("is_xmas")
            if is_xmas:
                quantity = info.get("quantity")
                xmas_text = f"__Xmas:__ **{i}** | Quantity: {quantity}"
                lst.append(xmas_text)
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)                
            is_item = info.get("is_item")
            if is_item:
                quantity = info.get("quantity")
                item_text = f"__Item:__ **{i}** | Quantity: {quantity}"
                lst.append(item_text)
        for i in inventory:
            info = await self.config.member(ctx.author).inventory.get_raw(i)                
            is_game = info.get("is_game") 
            if is_game:           
                quantity = info.get("quantity")
                game_text = f"__Game:__ **{i}** | Quantity: {quantity}"
                lst.append(game_text)                
        if lst == []:
            desc = "Nothing to see here, go buy something at the `!shop`"
        else:
            desc = ("\n".join(lst))
        embed = discord.Embed(
            colour=await ctx.embed_colour(),
            description=str(desc),
            timestamp=datetime.now(),
        )
        embed.set_author(
            name=f"{ctx.author.display_name}'s inventory", icon_url=ctx.author.avatar_url,
        )            
        embed.set_footer(text="Inventory™")
        await ctx.send(embed=embed) 
        
    @commands.command()
    @commands.guild_only()
    async def gift(self, ctx: commands.Context, user: discord.Member, quantity: int, *, item: str = ""):
        """Gift another user a Christmas Present!
        
        Examples
        --------
        `!gift @ThalamusZen 2 Small gift`
        """
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop is closed. Come back later!")        
        if quantity < 1:
            return await ctx.send("Think you're smart huh?")
        if user == ctx.author:
            return await ctx.send("Maybe you should find some friends.")
        if user == ctx.bot.user:
            return await ctx.send("No thank you, why don't you give it to Zen instead?")
        author_inv = await self.config.member(ctx.author).inventory.get_raw()
        if item in author_inv:
            pass
        else:
            return await ctx.send("You don't own this item.")
        info = await self.config.member(ctx.author).inventory.get_raw(item)
        giftable = info.get("giftable")
        if not giftable:
            return await ctx.send("This are not able to gift this item.")
        gifted = info.get("gifted")
        if gifted:
            return await ctx.send("You cannot gift an item that was gifted to you... rude.")
        author_quantity = int(info.get("quantity"))
        author_price = int(info.get("price"))
        if author_quantity < quantity:
            return await ctx.send(f"You don't have that many {item} to give.")
        author_quantity -= quantity
        if author_quantity == 0:
            await self.config.member(ctx.author).inventory.clear_raw(item)
        else:            
            await self.config.member(ctx.author).inventory.set_raw(
                item, "quantity", value=author_quantity
            )
        giftee_inv = await self.config.member(user).inventory.get_raw()
        from_text = " from "
        iu = []
        iu.append(item)
        iu.append(from_text)
        iu.append(str(ctx.author.name))
        item_user = ''.join(iu)
        if item_user in giftee_inv:
            info = await self.config.member(user).inventory.get_raw(item_user)
            giftee_quantity = info.get("quantity")
            giftee_quantity += quantity
            await self.config.member(user).inventory.set_raw(
                item_user, "quantity", value=giftee_quantity
            )
        else:
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
        `!open Small gift from Thalamus Zen`
        """
        enabled = await self.config.guild(ctx.guild).enabled()
        if not enabled:
            return await ctx.send("Uh oh, the shop module is disabled. Come back later!")
#       LOOK INTO THE ENABLED FEATURE ABOVE SOULD I TOGGLE OR USE THE DATE       
        author_inv = await self.config.member(ctx.author).inventory.get_raw()
        if item in author_inv:
            pass
        else:
            return await ctx.send("You don't own this item.")
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
        await ctx.send("Wibble wobble") 
#	NEED TO EXTRACT GIFTER FROM GIFT COMMAND AND APPLY IT TO SOMEWHERE BELOW
        placing_messages = [
            "*You excitedly place the gift upon your lap and smile...*",
            "*You slide out the present from beneath the Christmas tree...*",
        ]
        bot_talking = await message.channel.send(random.choice(placing_messages))
        await asyncio.sleep(random.randint(5, 8))
        opening_messages = [
            "*You are quick to rip the red and white wrapping paper from the present...*",
            "*You delicately tear the wrapping paper from around the present...*",
        ]
        await bot_talking.edit(content=random.choice(opening_messages))
        await asyncio.sleep(random.randint(5, 8))
        sg_messages = [
            f"{message.author.mention} You received: Socks",
            f"{message.author.mention} You received: Deodorant",
        ]
        mg_messages = [
            f"{message.author.mention} You received: Overwatch 2",
            f"{message.author.mention} You received: A £10 Steam gift card",
        ]
        size = info.get("size")
        if size == small:
            await asyncio.sleep(2)
            await message.channel.send(content=random.choice(sg_messages))
        if size == medium:
            await asyncio.sleep(2)
            await message.channel.send(content=random.choice(mg_messages))             

    @commands.command()
    @commands.guild_only()
    async def removeinventory(self, ctx: commands.Context, *, item: str):
        """Remove an item from your inventory."""
        inventory = await self.config.member(ctx.author).inventory.get_raw()
        if item not in inventory:
            return await ctx.send("You don't own this item.")
        await self.config.member(ctx.author).inventory.clear_raw(item)
        await ctx.send(f"{item} removed.")

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
            return await ctx.send("Uh oh, your Admins haven't set this yet.")
        ping = get(ctx.guild.members, id=ping_id)
        if not ping:
            ping = get(ctx.guild.roles, id=ping_id)
            if not ping:
                return await ctx.send("Uh oh, your Admins haven't set this yet.")
            if not ping.mentionable:
                await ping.edit(mentionable=True)
                await ctx.send(
                    f"{ping.mention}, {ctx.author.mention} would like to redeem {item}."
                )
                await ping.edit(mentionable=False)
            else:
                await ctx.send(
                    f"{ping.mention}, {ctx.author.mention} would like to redeem {item}."
                )
            await self.config.member(ctx.author).inventory.set_raw(
                item, "redeemed", value=True
            )
        else:
            await ctx.send(
                f"{ping.mention}, {ctx.author.mention} would like to redeem {item}."
            )
            await self.config.member(ctx.author).inventory.set_raw(
                item, "redeemed", value=True
            )

    async def _show_store(self, ctx):
        items = await self.config.guild(ctx.guild).items.get_raw()
        roles = await self.config.guild(ctx.guild).roles.get_raw()
        games = await self.config.guild(ctx.guild).games.get_raw()
        xmas = await self.config.guild(ctx.guild).xmas.get_raw()
        credits_name = await bank.get_currency_name(ctx.guild)
        stuff = []
        for r in roles:
            role = await self.config.guild(ctx.guild).roles.get_raw(r)
            priceint = int(role.get("price"))
            price = humanize_number(priceint)
            quantity = int(role.get("quantity"))
            role_name = role.get("role_name")
            role_text = f"__Role:__ **{r}** | __Price:__ {price} {credits_name} | __Quantity:__ {quantity} | __Looks like:__ {role_name}"
            stuff.append(role_text)
        for i in items:
            item = await self.config.guild(ctx.guild).items.get_raw(i)
            priceint = int(item.get("price"))
            price = humanize_number(priceint)
            quantity = int(item.get("quantity"))
            item_text = f"__Item:__ **{i}** | __Price:__ {price} {credits_name} | __Quantity:__ {quantity}"
            stuff.append(item_text)
        for g in games:
            game = await self.config.guild(ctx.guild).games.get_raw(g)
            priceint = int(game.get("price"))
            price = humanize_number(priceint)
            quantity = int(game.get("quantity"))
            game_text = f"__Item:__ **{g}** | __Price:__ {price} {credits_name} | __Quantity:__ {quantity}"
            stuff.append(game_text)
        for x in xmas:
            xmas = await self.config.guild(ctx.guild).xmas.get_raw(x)
            priceint = int(xmas.get("price"))
            price = humanize_number(priceint)
            quantity = int(xmas.get("quantity"))
            xmas_text = f"__Xmas:__ **{x}** | __Price:__ {price} {credits_name} | __Quantity:__ {quantity}"
            stuff.append(xmas_text)
        if stuff == []:
            desc = "Nothing to see here."
        else:
            predesc = "`Syntax !buy <quantity> <item_name>`\n\nWhen using the `!buy` command, please be aware that items are **case sensitive**.\nTo remove a role from yourself, it must be returned to the shop and can be done so with the `!return <role name>` command.\nReturning roles will give you a 10% refund on what you originally paid.\n\n"
            desc = predesc + ("\n".join(stuff))
        page_list = []
        for page in pagify(desc, delims=["\n"], page_length=1000):
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                description=page,
                timestamp=datetime.now(),
            )
            embed.set_author(
                name=f"{ctx.guild.name}'s shop", icon_url=ctx.guild.icon_url,
            )
            embed.set_footer(text="Shoppy™")
            page_list.append(embed)
        return page_list
