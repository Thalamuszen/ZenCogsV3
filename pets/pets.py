import asyncio
import datetime
import discord
import logging
import random

from random import uniform, randint
from discord.utils import get
from datetime import datetime, timezone
from tabulate import tabulate
from operator import itemgetter

from redbot.core import commands, checks, Config, bank
from redbot.core.utils.chat_formatting import box, humanize_list, pagify

from redbot.core.bot import Red

log = logging.getLogger("red.zen.pets")

#Attitude values. Positive INT, Positive Desc. Negative INT, Negative Desc.
#INTs refer to how much they change a particular value.
ATTITUDE = {
    "Clingy": [0, "Description", 0, "Description"],
    "Ditzy": [0, "Description", 0, "Description"],
    "Grumpy": [0, "Description", 0, "Description"],
    "Happy": [0, "Description", 0, "Description"],
}

#Health bar emojis.
HEALTHBAR = {
    "left_full": "<:Health_left:781137677680246794>",
    "mid_full": "<:Health_mid:781137677684178974>",
    "right_full": "<:Health_right:781137677525319691>",
}

#Empty bar emojis.
BAREMPTY = {
    "left_empty": "<:Empty_left:781138077354819584>",
    "mid_empty": "<:Empty_mid:781138077380771860>",
    "right_empty": "<:Empty_right:781138077380902932>",
}

class Pets(commands.Cog):
    async def red_delete_data_for_user(self, **kwargs):
        """ Nothing to delete """
        return

    __author__ = "ThalamusZen"
    __version__ = "0.6.9"    

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, 4119811374891, force_registration=True)

        default_guild = {
            "enabled": False, 
            "cooldown": 30, 
            "pets": {}, 
            "beasts": {}, 
            "mounts":{}, 
            "rares":{}, 
            "abilities":{},
        }

        default_member = {
            "pets": {},
            "beasts": {},
            "mounts": {},
            "rares": {},
            "pet": 0,
            "beast": 0,
            "mount": 0,
            "rare": 0, 
        }

        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)       

    @commands.group(autohelp=True)
    @checks.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def pets(self, ctx):
        """Admin pets settings."""
        pass

    @pets.command(name="toggle")
    async def pets_toggle(self, ctx: commands.Context, on_off: bool = None):
        """Toggle pets for the current server.
        If `on_off` is not provided, the state will be flipped."""
        target_state = (
            on_off
            if on_off
            else not (await self.config.guild(ctx.guild).enabled())
        )
        await self.config.guild(ctx.guild).enabled.set(target_state)
        if target_state:
            await ctx.send("Pets is now enabled.")
        else:
            await ctx.send("Pets is now disabled.")

    @pets.command(name="add")
    async def pets_add(self, ctx: commands.Context):
        """Add a pet/beast/mount/bonus."""

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        types = ["pet", "beast", "mount", "rares"]
        pred_type = MessagePredicate.lower_contained_in(types)
        pred_int = MessagePredicate.valid_int(ctx)
        pred_yn = MessagePredicate.yes_or_no(ctx)

        await ctx.send(
            "Do you want to add an `pet`, `beast`, `mount` or a `rare` animal to the database?\n"
            "__**Pets**__: Stay at home animal. For cuddles, feeding, taking for a walk, you get the idea.\n"
            "__**Beasts**__: An animal that fights along side the user. Adventure module coming soon™\n"
            "__**Mounts**__: An animal used to travel faster within the aforemention Adventure module.\n"
            "__**Rares**__: A rare animal that is considered a lucky charm. Requires no maintenance.\n"
            "**NOTE** Rare animals have abilities that are hardcoded into other modules.\n"
            "**Members of your guild can only have one of each at any given time.**\n"
        )
        try:
            await self.bot.wait_for("message", timeout=30, check=pred_type)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        animal_cat = answer.content      
#Add pet.        
        if pred.result == 0:
            await ctx.send(
                "What is the name of the pet?"
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            pet_name = answer.content
            lower_pet_name = answer.content.lower()
            try:
                check_pet = await self.config.guild(ctx.guild).pets.get_raw(
                    lower_pet_name
                )
                if is_already_pet:
                    return await ctx.send(
                        "This pet already exists. Please, remove it first or try again."
                    )
            except KeyError:
                await ctx.send("What type of pet is this? Cat|Dog|Hamster etc.")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                pet_type = answer.content
#Set breed for the pet.
                await ctx.send(f"What breed of {pet_type} is this?")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                breed = answer.content       
#Set price for the pet. Shop.
                await ctx.send("How much should this pet cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")
#Set quantity for the pet. Shop.
                await ctx.send("What quantity of this pet should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
#Set Tuhumbnail URL for the pet.
                await ctx.send("Thumbnail URL (preferably a Discord URL) Try to use a square image.")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                thumbnail_url = answer.content
#Set Image URL for the pet.
                await ctx.send("Image URL (preferably a Discord URL) Try to use a square image.")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                image_url = answer.content
#Set the pets description.
                await ctx.send("Give the pet a description")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                description = answer.content
                description = description.strip("@")
#Add pet to the DB.                
                await self.config.guild(ctx.guild).items.set_raw(
                    lower_pet_name,
                    value={
                        "category": animal_cat,                        
                        "type": pet_type, 
                        "breed": breed,
                        "name": pet_name,                       
                        "user_name": "",
                        "lower_user_name": "",
                        "price": price,
                        "quantity": quantity,
                        "xp": 0,
                        "hunger": 100,
                        "dirtiness": 0,
                        "affection": 10,
                        "fatigue": 0,
                        "attitude": "happy",
                        "thumbnail": thumbnail_url,
                        "image": image_url,
                        "description": description,             
                    },
                )
                await ctx.send(f"{pet_name} added.")
#Add Beast.                
        if pred.result == 1:
            await ctx.send(
                "What is the name of the beast? Warg, unicorn? Etc."
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            beast_name = answer.content
            lower_beast_name = answer.content.lower()
            try:
                is_already_beast = await self.config.guild(ctx.guild).pets.get_raw(
                    lower_beast_name
                )
                if is_already_beast:
                    return await ctx.send(
                        "This beast already exists. Please, remove it first or try again."
                    )
            except KeyError:
#PRICE REMOVE.                
                await ctx.send("How much should this item cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")
#QUANTITY REMOVE.                
                await ctx.send("What quantity of this item should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
#REDEEMABLE REMOVE.                
                await ctx.send("Is the item redeemable?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                redeemable = pred_yn.result
#Set description for the beast.                
                await ctx.send("Give the beast a description")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                description = answer.content
                description = description.strip("@")
#Add beast to DB.                
                await self.config.guild(ctx.guild).items.set_raw(
                    lower_beast_name,
                    value={
                        "type": animal_type,
                        "name": pet_name,
                        "xp": 0,
                        "health": health,
                        "hunger": hunger,
                        "dirtiness": 0,
                        "affection": 10,
                        "fatigue": 0,
                        "attitude": "happy",
                        "bonus":{
                            "bonus1": [bonus1_yn, bonus1_desc],
                            "bonus2": [bonus2_yn, bonus2_desc],
                            "bonus3": [bonus3_yn, bonus3_desc],
                        },
                        "image": image_url,
                        "description": description,             
                    },
                )
                await ctx.send(f"{beast_name} added.")
#Add mount.                
        if pred.result == 2:
            await ctx.send(
                "What is the name of the mount?"
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            mount_name = answer.content
            lower_mount_name = answer.content.lower()
            try:
                is_already_mount = await self.config.guild(ctx.guild).pets.get_raw(
                    lower_mount_name
                )
                if is_already_mount:
                    return await ctx.send(
                        "This mount already exists. Please, remove it first or try again."
                    )
            except KeyError:
#COST/PRICE REMOVE.
                await ctx.send("How much should this item cost?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                price = pred_int.result
                if price <= 0:
                    return await ctx.send("Uh oh, price has to be more than 0.")               
#QUANTITY REMOVE
                await ctx.send("What quantity of this item should be available?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                quantity = pred_int.result
                if quantity <= 0:
                    return await ctx.send("Uh oh, quantity has to be more than 0.")
#Set mount description.
                await ctx.send("Give the mount a description")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                description = answer.content
                description = description.strip("@") 
#Set mount if flying.
                await ctx.send("Can this mount fly?")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_yn)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                flying_yn = pred_yn.result
                if flying_yn == True:
                    await ctx.send("How fast can it fly? UNIT MEASUREMENT OF FLYING SPEED, WHICH IS SAME AS GROUND SPEED.")
                    try:
                        await self.bot.wait_for("message", timeout=120, check=pred_int)
                    except asyncio.TimeoutError:
                        return await ctx.send("You took too long. Try again, please.")
                    fly_speed = pred_int.result
                    await self.config.guild(ctx.guild).items.set_raw(
                        lower_mount_name,
                        value={
                            "type": animal_type,
                            "name": mount_name,
                            "xp": 0,
                            "health": health,
                            "hunger": hunger,
                            "dirtiness": 0,
                            "affection": 10,
                            "fatigue": 0,
                            "attitude": "happy",
                            "flying": [flying_yn, fly_speed],
                            "image": image_url,
                            "description": description,             
                        },
                    )
                    await ctx.send(f"{mount_name} added.")
                else:  
                    await self.config.guild(ctx.guild).items.set_raw(
                        pet_name,
                        value={
                            "type": animal_type,
                            "name": pet_name,
                            "xp": 0,
                            "health": health,
                            "hunger": hunger,
                            "dirtiness": 0,
                            "affection": 10,
                            "fatigue": 0,
                            "attitude": "happy",
                            "image": image_url,
                            "description": description,             
                        },
                    )
                    await ctx.send(f"{mount_name} added.")
#Add rare.        
        if pred.result == 3:                        
            await ctx.send(
                "What is the name of the rare?"
            )
            try:
                answer = await self.bot.wait_for("message", timeout=120, check=check)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            rare_name = answer.content
            lower_rare_name = answer.content.lower()
            try:
                is_already_rare = await self.config.guild(ctx.guild).rares.get_raw(
                    lower_rare_name
                )
                if is_already_rare:
                    return await ctx.send(
                        "This rare already exists. Please, remove it first or try again."
                    )
            except KeyError:
                await ctx.send("What type of rare is this? Fairy|Mermaid|Unicorn etc.")
                try:
                    answer = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                rare_type = answer.content                               
#Set affection for rare.
                await ctx.send("Starting affection? Number only.")
                try:
                    await self.bot.wait_for("message", timeout=120, check=pred_int)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                affection = pred_int.result
                if affection < 0:
                    return await ctx.send("The affection level has to be 0 or more than 0.")
#Set attitude for rare.
                await ctx.send("What is the consistant attitude of the rare? Happy|Sad|Angry whatever you like.")
                try:
                    answer = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                attitude = answer.content
#Ability section process for rare.
                abilities = await self.config.guild(ctx.guild).abilities.get_raw(a)                
                ablist = []
                for a in abilities:
                    ability = await self.config.guild(ctx.guild).abilities.get_raw(a)
                    name = ability.get("name")  
                    description = abilty.get("description")                   
                    table = [a, name, description]
                    ablist.append(table)
                    sorted_ablist = sorted(ablist, key=itemgetter(0))
                if ablist == []:
                    table = ["", "", "No abilities have been added. Run !pets ability <ability_name> to get started."]
                    ablist.append(table)
                    sorted_ablist = sorted(ablist, key=itemgetter(0))                    
                headers = ("Name", "Name", "Description")
                output = box(tabulate(sorted_ablist, headers=headers), lang="md")
                await ctx.send(
                    (
                        "Choose an ability to give the rare.\n" 
                        "{output}\n"
                        "Can't see an ability you want? Add it yourself using `!pets abilities`"
                    ).format(
                        output=output,
                    )
                )
                try:
                    answer = await self.bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")                
                lower_ability_name = answer.content.lower()
                try:
                    check_ability = await self.config.guild(ctx.guild).abilities.get_raw(lower_ability_name)
                    if check_ability:                        
                        ability = check_ability.get("name")
                except KeyError:
                    return await ctx.send(
                        "This ability doesn't exist. Please create one using `!pets abilities` or type it in correctly."
                    )                        
#Set Thumbnail URL for rare.
                await ctx.send("Thumbnail URL (preferably a Discord URL) Try to use a square image.")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                thumbnail_url = answer.content
#Set Image URL for Rare.
                await ctx.send("Image URL (preferably a Discord URL) Try to use a square image.")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                image_url = answer.content
#Set the description for the rare.
                await ctx.send("Give the rare a description")
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                description = answer.content
#Adds the rare animal to the DB.
                await self.config.guild(ctx.guild).rares.set_raw(
                    lower_rare_name,
                    value={
                        "category": animal_cat,
                        "type": rare_type,
                        "name": rare_name,
                        "user_name": "",
                        "lower_user_name": "",
                        "affection": 10,
                        "attitude": attitude,
                        "ability": ability,
                        "thumbnail": thumbnail_url,
                        "image": image_url,
                        "description": description,             
                    },
                )
                await ctx.send(f"{rare_name} added.")
        else:
            await ctx.send("This answer is not supported. Try again, please.") 

    @pets.command(name="remove")
    async def pets_remove(self, ctx: commands.Context, *, animal: str):
        """Remove a pet/beast/mount/rare animal from the guild database."""
        animal = animal.lower()
        try:
            is_already_pet = await self.config.guild(ctx.guild).pets.get_raw(animal)
            if is_already_pet:
                await self.config.guild(ctx.guild).pets.clear_raw(animal)
                return await ctx.send(f"{animal} removed.")
        except KeyError:
            try:
                is_already_beast = await self.config.guild(ctx.guild).beasts.get_raw(animal)
                if is_already_beast:
                    await self.config.guild(ctx.guild).beasts.clear_raw(animal)
                    return await ctx.send(f"{animal} removed.")
            except KeyError:
                try:
                    is_already_mount = await self.config.guild(ctx.guild).mounts.get_raw(animal)
                    if is_already_mount:
                        await self.config.guild(ctx.guild).mounts.clear_raw(animal)
                        await ctx.send(f"{animal} removed.")
                except KeyError:
                    try:
                        is_already_rare = await self.config.guild(ctx.guild).rares.get_raw(animal)
                        if is_already_rare:
                            await self.config.guild(ctx.guild).rares.clear_raw(animal)
                            return await ctx.send(f"{animal} removed.")
                    except KeyError:
                        await ctx.send(f"Can't find {animal} in the guild database.")
    
    @pets.command(name="list")
    async def pets_list(self, ctx:commands.Context, *, type: str):
        """Show a list of pets/beasts/mounts/rares or all from the guild Database."""
        pets = await self.config.guild(ctx.guild).pets.get_raw()
        beasts = await self.config.guild(ctx.guild).beatss.get_raw()
        mounts = await self.config.guild(ctx.guild).mounts.get_raw()
        rares = await self.config.guild(ctx.guild).rares.get_raw()
        pets_table = []
        sorted_pets = []
        beasts_table = []
        sorted_beasts = []
        mounts_table = []
        sorted_mounts = []
        rares_table = []
        sorted_rares = []
        all_table = []
        sorted_all = []
        type = type.lower()
        if type == "pets":
            for p in pets:
                pet = await self.config.guild(ctx.guild).pets.get_raw(p)
                quantity = int(pet.get("quantity"))
                table = [r, quantity, role_name]
                pets_table.append(table)
                sorted_pets = sorted(pets_table, key=itemgetter(0))
        if sorted_pets == []:
            await ctx.send ("Nothing to see here!")
        else:                
            headers = ("Name", "Type")
            output = box(tabulate(sorted_pets, headers=headers), lang="md")
            return await ctx.send (f"{output}")                   
        if type == "beasts":
            for b in beasts:
                beast = await self.config.guild(ctx.guild).beasts.get_raw(b)
                quantity = int(beast.get("quantity"))
                table = [b, quantity, role_name]
                beasts_table.append(table)
                sorted_beasts = sorted(beasts_table, key=itemgetter(0))
        if sorted_beasts == []:
            await ctx.send ("Nothing to see here!")
        else:                
            headers = ("Name", "Type")
            output = box(tabulate(sorted_beasts, headers=headers), lang="md")
            return await ctx.send (f"{output}")                   
        if type == "mounts":
            for m in mounts:
                mount = await self.config.guild(ctx.guild).mounts.get_raw(m)
                quantity = int(mount.get("quantity"))
                table = [m, quantity, role_name]
                mounts_table.append(table)
                sorted_mounts = sorted(mounts_table, key=itemgetter(0))
        if sorted_mounts == []:
            await ctx.send ("Nothing to see here!")
        else:                
            headers = ("Name", "Type")
            output = box(tabulate(sorted_mounts, headers=headers), lang="md")
            return await ctx.send (f"{output}")   
        if type == "rares":
            for r in rares:
                rare = await self.config.guild(ctx.guild).mounts.get_raw(r)
                quantity = int(rare.get("quantity"))
                table = [r, quantity, role_name]
                rares_table.append(table)
                sorted_rares = sorted(rares_table, key=itemgetter(0))
        if sorted_rares == []:
            await ctx.send ("Nothing to see here!")
        else:                
            headers = ("Name", "Type")
            output = box(tabulate(sorted_rares, headers=headers), lang="md")
            return await ctx.send (f"{output}")                                    
        if type == "all":
            for a in allofthem:
                pet = await self.config.guild(ctx.guild).pets.get_raw(a)
                animal_type = pet.get("type")                
                beast = await self.config.guild(ctx.guild).beasts.get_raw(a)
                animal_type = beast.get("type")  
                mount = await self.config.guild(ctx.guild).mounts.get_raw(a)
                animal_type = mount.get("type")  
                rare = await self.config.guild(ctx.guild).mounts.get_raw(a)
                animal_type = rare.get("type")  
                table = [a, animal_type]
                all_table.append(table)
                sorted_all = sorted(all_table, key=itemgetter(0))
        if sorted_all == []:
            await ctx.send ("Nothing to see here!")
        else:                
            headers = ("Name", "Type")
            output = box(tabulate(sorted_all, headers=headers), lang="md")
            await ctx.send (f"{output}") 

    @pets.command(name="show")
    async def pets_show(self, ctx: commands.Context, *, animal: str):
        """Show information about a pet/beast/mount/rare from the guild database."""
        animal = animal.strip("@")
        pets = await self.config.guild(ctx.guild).pets.get_raw()
        beasts = await self.config.guild(ctx.guild).beasts.get_raw()
        mounts = await self.config.guild(ctx.guild).mounts.get_raw()
        rares = await self.config.guild(ctx.guild).rares.get_raw()

        if animal in pets:
            info = await self.config.guild(ctx.guild).pets.get_raw(animal)
            animal_type = "Pet"
        elif animal in beasts:
            info = await self.config.guild(ctx.guild).beasts.get_raw(animal)
            animal_type = "Beast"
        elif animal in mounts:
            info = await self.config.guild(ctx.guild).mounts.get_raw(animal)
            animal_type = "Mount"
        elif animal in rares:
            info = await self.config.guild(ctx.guild).rares.get_raw(animal)
            animal_type = "Rare"            
        else:
            return await ctx.send(f"{animal} isn't in the guild database.")
        price = info.get("price")
        quantity = info.get("quantity")
        redeemable = info.get("redeemable")
        description = info.get("description")
        size = info.get("size")
        if not redeemable:
            redeemable = False
        await ctx.send(
            f"**__{animal}:__**\n**Type:** {animal_type}\n**Price:** {price}\n**Quantity:** {quantity}\n**Redeemable:** {redeemable}\n**Description:** {description}\n**Xmas gift size:** {size}"
        )

    @pets.command(name="reset")
    async def all_pets_reset(self, ctx: commands.Context, member: discord.Member):
        """Reset all pets for a single user."""
        try:
            pets = await self.config.member(member).pets.get_raw()
            for pet in pets:
                await self.config.member(member).pets.clear_raw(pet)        
        except KeyError:
            pass
        try:
            beasts = await self.config.member(member).beasts.get_raw()
            for beast in beasts:
                await self.config.member(member).beast.clear_raw(beast)
        except KeyError:
            pass
        try:
            mounts = await self.config.member(member).mounts.get_raw()
            for mount in mounts:
                await self.config.member(member).mounts.clear_raw(mount)
        except KeyError:
            pass
        try:
            rares = await self.config.member(member).rares.get_raw()
            for rare in rares:
                await self.config.member(member).rares.clear_raw(rare)                             
        except KeyError:
            pass
        userdata = await self.config.member(member).all()
        if userdata["pet"]:
            number = userdata['pet']
            await self.config.member(member).pet.set(userdata["pet"] - number)
        userdata = await self.config.member(member).beasts.get_raw()
        if userdata["beast"]:    
            number = userdata['beast']            
            await self.config.member(member).beast.set(userdata["beast"] - number)
        userdata = await self.config.member(member).mounts.get_raw()
        if userdata["mount"]:     
            number = userdata['mount']            
            await self.config.member(member).mount.set(userdata["mount"] - number)
        userdata = await self.config.member(member).rares.get_raw()
        if userdata["rare"]:  
            number = userdata['rare']            
            await self.config.member(member).rare.set(userdata["rare"] - number)
        await ctx.send(f"{member.name}'s pets data has been wiped.")

    @pets.command(name="abilities")
    async def pets_abilities(self, ctx: commands.Context):
        """Shows a list of abilities that have been created"""
        abilities = await self.config.guild(ctx.guild).abilities.get_raw()        
        ablist = []
        for a in abilities:
            ability = await self.config.guild(ctx.guild).abilities.get_raw(a)
            name = ability.get("name")  
            description = ability.get("description")                   
            table = [a, name, description]
            ablist.append(table)
            sorted_ablist = sorted(ablist, key=itemgetter(0))
        if ablist == []:
            table = ["", "", "No abilities have been added. Run !pets ability <ability_name> to get started."]
            ablist.append(table)
            sorted_ablist = sorted(ablist, key=itemgetter(0))
        headers = ("Name", "Name", "Description")
        output = box(tabulate(sorted_ablist, headers=headers), lang="md")            
        await ctx.send(
            (
                "{output}"
            ).format(
                output=output,
            )
        )        

    @pets.command(name="ability")
    async def pets_ability(self, ctx: commands.Context, *, ability: str):
        """Creates a new ability which can be given to your animals during the `!pets add` process."""       
        ability_lower = ability.lower()
        abilities = await self.config.guild(ctx.guild).abilities.get_raw() 
        try:
            check_ability = await self.config.guild(ctx.guild).abilities.get_raw(ability_lower)
            if check_ability:
                ablist = []
                for a in abilities:
                    ability = await self.config.guild(ctx.guild).abilites.get_raw(a)
                    name = ability.get("name")  
                    description = ability.get("description")                   
                    table = [a, name, description]
                    ablist.append(table)
                    sorted_ablist = sorted(ablist, key=itemgetter(0))
                headers = ("Name", "Name", "Description")
                output = box(tabulate(sorted_ablist, headers=headers), lang="md")                                 
                await ctx.send(f"{ability_lower} already exists.\n{output}")
        except KeyError:                
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                await ctx.send(
                    "What is the description of the ability."
                )
                try:
                    answer = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")                
                await self.config.guild(ctx.guild).abilities.set_raw(
                    ability_lower, value={"name": ability, "description": description}
                )                
                await ctx.send(f"{ability_lower} has been added succesfully.\nRun `!pets abilities to see the full list.")
