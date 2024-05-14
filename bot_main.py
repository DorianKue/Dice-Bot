import discord
from discord import Intents
from discord.ext import commands
from discord.ui import View
import math
from random import randint, choice
from dotenv import load_dotenv
import logging
import os
import csv
import asyncio
import re
from character import Character
from components.lvl_buttons import MyView
from commands.help import CustomHelpCommand
from components.rm_buttons import RView
from components.racebuttons import RCView
from components.rnd_char import RandView


async def get_custom_prefix(bot, message):
    """
    Retrieves the custom prefix for the given message's guild from a CSV file.

    Args:
        bot (discord.ext.commands.Bot): The bot instance.
        message (discord.Message): The message object for which to retrieve the prefix.

    Returns:
        str: The custom prefix for the guild, or '/' if not found.
    """
    # Define the filename for the prefixes CSV file
    prefixes_file = "prefixes.csv"

    # Check if the message was sent in a guild (server)
    if message.guild:
        # Construct the full path to the prefixes CSV file
        prefixes_file_path = os.path.join("resources", prefixes_file)

        # Check if the prefixes CSV file exists
        if os.path.exists(prefixes_file_path):
            # Open the prefixes CSV file
            with open(prefixes_file_path) as file:
                # Read the CSV file as a dictionary
                reader = csv.DictReader(file)

                # Iterate through each row in the CSV file
                for row in reader:
                    # Check if the ServerID in the row matches the guild's ID
                    if int(row["ServerID"]) == message.guild.id:
                        # Return the custom prefix for the guild
                        return row["Prefix"]

    # Return '/' as the default prefix if no custom prefix is found
    return "/"


def create_logs_directory():
    logs_dir = "Bot/Dice-Bot/logs"
    os.makedirs(logs_dir, exist_ok=True)


def bot_setup():
    # Load environment variables from the .env file
    load_dotenv()

    # Get Discord token from environment variable
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Create Discord bot instance with specified intents
    intents = Intents.default()
    intents.message_content = True
    bot = commands.Bot(
        command_prefix=get_custom_prefix,  # Define the prefix for command invocation
        intents=intents,  # Specify the intents for the bot to receive from Discord
        help_command=None,  # Disable the default help command
        case_insensitive=True,  # Make commands case-insensitive
    )
    create_logs_directory()
    handler = logging.FileHandler(
        filename="Bot/Dice-Bot/logs/discord.log", encoding="utf-8", mode="w"
    )
    return bot, TOKEN, handler


bot, TOKEN, handler = bot_setup()
# Create an instance of the CustomHelpCommand class and pass the bot instance to it
# This allows the custom help command to access bot-related functionality
custom_help_command = CustomHelpCommand(bot)


# Helper function to get the ID of the character creator
async def get_character_creator_id(char_name, server_id):
    """
    Get the ID of the user who created the character.

    Args:
        char_name (str): The name of the character.
        server_id (int): The ID of the server where the character belongs.

    Returns:
        int: The ID of the user who created the character.
    """
    # Construct directory path based on server ID
    server_dir = f"server_{server_id}"
    saves_dir = os.path.join("resources", "saves", server_dir)
    # Construct the full file path
    filepath = os.path.join(saves_dir, f"{char_name.lower()}_stats.csv")

    # Check if the character's stats file exists
    if not os.path.isfile(filepath):
        return None
    else:
        # Load the creator ID from the CSV file
        with open(filepath, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                creator_id = None
                if row["Name"].lower() == char_name.lower():
                    if creator_id is None:
                        creator_id = row["CreatorID"]
                        return creator_id
    return None


async def disable_button(button_id):
    async def predicate(interaction):
        if interaction.data["custom_id"] == button_id:
            return True
        return False

    return predicate


async def help_cogs(ctx):
    """
    Asynchronously adds the CustomHelpCommand cog to the bot.

    Args:
        ctx (commands.Context): The context representing the invocation context of the command.

    Returns:
        None
    """
    await bot.add_cog(CustomHelpCommand(bot))


@bot.event
async def on_ready():
    """Print a message when the bot is ready."""
    game = discord.Game("with Dice")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Bot is ready.")


@bot.event
async def on_message(message):
    """Process incoming messages."""
    if message.author.id == bot.user.id:
        return
    # Call update_commands whenever a new CSV file is created
    if message.attachments:  # Check if there are any attachments in the message
        for attachment in message.attachments:  # Iterate through each attachment
            if attachment.filename.endswith(
                ".csv"
            ):  # Check if the attachment is a CSV file
                await update_commands()  # Call update_commands function
    await bot.process_commands(message)  # Process bot commands


@bot.event
async def on_command_error(ctx, error):
    """Handle errors that occur during command invocation."""
    if isinstance(error, commands.CommandNotFound):
        # Do nothing or send a custom message
        pass
    else:
        # Handle other errors
        await ctx.send(f"An error occurred: {error}", ephemeral=True)


async def update_commands():
    """
    Update the bot commands based on available character stats CSV files.
    """
    # Get the directory path where the bot's code resides
    bot_directory = os.path.dirname(os.path.realpath(__file__))
    prefix_folder = os.path.join(bot_directory, "resources")
    prefixes_file_path = os.path.join(prefix_folder, "prefixes.csv")
    # Iterate through files in the directory
    for filename in os.listdir(bot_directory):
        # Check if the file is a CSV file
        if filename.endswith(".csv"):
            # Extract character name from the filename
            character_name = filename[:-10]

            # Define a wrapper function for displaying character stats
            async def display_character_stats_wrapper(
                ctx, char_name=character_name, server_id=None
            ):
                """
                Wrapper function for displaying character stats.

                Args:
                    ctx: The context object representing the invocation context.
                    char_name (str): The name of the character.
                    server_id: The ID of the server where the character belongs.
                """
                # Use the provided server_id or get it from the context if not provided
                server_id = server_id or ctx.guild.id
                # Call the display_character_stats function with the provided arguments
                await Character.display_character_stats(ctx, char_name, server_id)

            # Create a bot command using the character name and the wrapper function
            bot.command(name=f"{character_name}_stats")(display_character_stats_wrapper)


@bot.hybrid_command(
    name="help", description="Shows all available commands and how to use them."
)
async def help(ctx):
    try:
        help_embed = await custom_help_command.send_bot_help(ctx, None)
        await ctx.send(embed=help_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="roll",
    description="Roll X number of dice with Y number of sides and an optional modifier. E.g. /roll 4d6 or /roll 4d6+2",
)
async def norm_roll(ctx, *, roll_input):
    """
    Roll a specified number of dice with a specified number of sides and an optional modifier.

    Args:
        ctx: The context object representing the invocation context.
        roll_input (str): The input specifying the number of dice, sides, and optional modifier (e.g., '2d6', '4d6+2', '3d10-1').
    """
    # Define a regular expression pattern to match the roll input format
    pattern = r"(\d+)d(\d+)([+-]\d+)?"

    # Try to match the input against the pattern
    match = re.match(pattern, roll_input)
    if match:
        # Extract the number of dice, sides, and modifier (if any)
        num_dice = int(match.group(1))  # Extract the number of dice
        sides = int(match.group(2))  # Extract the number of sides
        modifier_str = match.group(3)  # Extract the modifier as a string
        modifier = 0  # Initialize modifier to 0
        if modifier_str:
            modifier = int(modifier_str)  # Convert the modifier string to an integer

        # Check if the number of dice is positive
        if num_dice <= 0:
            await ctx.send(
                "Please specify a positive number of dice.",
                ephemeral=True,
                delete_after=10,
            )
            return

        # Roll the dice and calculate the total
        rolls = [randint(1, sides) for _ in range(num_dice)]  # Roll the dice
        total = sum(rolls) + modifier  # Calculate the total by adding the modifier

        # Send the roll results to the channel
        if num_dice > 1:
            if not modifier_str:
                await ctx.send(
                    f"You rolled: {rolls}\nTotal: {total}"
                )  # Send rolls and total
            else:
                await ctx.send(
                    f"You rolled: {rolls}\nTotal with modifier: {total}"
                )  # Send rolls and total with modifier
        else:
            if not modifier_str:
                await ctx.send(
                    f"You rolled: {rolls}"
                )  # Send rolls only if one die rolled
            else:
                await ctx.send(
                    f"You rolled: {rolls}\nTotal with modifier: {total}"
                )  # Send rolls and total with modifier
    else:
        # Send error message for invalid input format
        await ctx.send(
            "Invalid input format. Please use the format 'XdY' or 'XdY+/-Z', where X is the number of dice, Y is the number of sides, and Z is the modifier.",
            ephemeral=True,
            delete_after=20,
        )


@bot.hybrid_command(
    name="roll_char",
    description="Create a character using dice rolls. Excludes the lowest roll! E.g. /roll_char 4d6 bob",
)
async def roll(ctx: discord.Interaction, roll_input: str, character_name: str):
    """
    Roll character stats based on input and provide an option to reroll.

    Args:
        ctx (discord.Interaction): The context of the command.
        roll_input (str): Input specifying the number of dice and sides (format: 'XdY').
        character_name (str): The name of the character being created.

    Raises:
        ValueError: If the input format for 'roll_input' is invalid.
        FileNotFoundError: If the character name already exists in the server directory.

    Returns:
        None
    """
    try:
        try:
            # Parse input to get number of dice and sides
            num_dice, sides = map(int, roll_input.split("d"))
        except ValueError:
            # Handle invalid input format
            await ctx.send(
                "Invalid input format. Please use the format 'XdY', where X is the number of dice and Y is the number of sides.",
                ephemeral=True,
                delete_after=20,
            )
            return

        # Check if the number of dice is positive
        if num_dice <= 0:
            await ctx.send(
                "Please specify a positive number of dice.",
                ephemeral=True,
                delete_after=10,
            )
            return

        server_dir = f"server_{ctx.guild.id}"
        saves_dir = os.path.join("resources", "saves", server_dir)
        # Check if the character name already exists
        if os.path.isfile(f"{saves_dir}/{character_name}_stats.csv"):
            await ctx.send(
                f"Character with name '{character_name}' already exists. Please choose a different name.",
                ephemeral=True,
                delete_after=30,
            )
            return

        # Create an instance of RCView for race selection
        raceview = await RCView.create(
            ctx,
            character_name,
            num_dice,
            sides,
            race_name=None,
            dndclass=None,
            dndclass_name=None,
            modifier=None,
        )

        # Send message to choose race with the created view
        message = await ctx.send("Choose your race:", view=raceview)

        # Wait for the user to click a button for race selection
        try:
            await bot.wait_for(
                "button_click",
                timeout=120,
                check=lambda interaction: ctx.message == message
                and interaction.user == ctx.author,
            )
        except asyncio.TimeoutError:
            # Handle timeout for race selection
            await raceview.on_timeout()
            await message.edit(content="Race selection timed out", view=raceview)
    except Exception as e:
        # Handle any other exceptions
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="random_char",
    description="Let the bot create a random character for you with 4d6 dice.",
)
async def random_roll(ctx: discord.Interaction, *, character_name: str):
    """
    Create a character with a random class and race, using 4d6 dice rolls.

    Args:
        ctx (discord.Interaction): The context object representing the invocation context.
        character_name (str): The name of the character.

    Returns:
        None
    """
    try:
        server_id = (
            ctx.guild.id
        )  # Get the ID of the server where the command was invoked
        invoker_id = ctx.author.id  # Get the ID of the user who invoked the command
        server_dir = (
            f"server_{ctx.guild.id}"  # Construct the directory name based on server ID
        )
        saves_dir = os.path.join(
            "resources", "saves", server_dir
        )  # Construct the directory path for saving character data

        # Check if the character name already exists
        if os.path.isfile(f"{saves_dir}/{character_name}_stats.csv"):
            await ctx.send(
                f"Character with name '{character_name}' already exists. Please choose a different name.",
                ephemeral=True,
                delete_after=30,
            )
            return

        # Create a RandView instance to handle the character creation UI
        randomview = RandView(ctx, character_name, server_id, invoker_id)

        # Send a message with the UI for creating a character and await a response
        random_char_msg = await randomview.create_char()
        full_msg = await ctx.send(
            f"{random_char_msg}Would you like to save this character?", view=randomview
        )

        # Wait for a button click from the user, with a timeout of 120 seconds
        try:
            await bot.wait_for(
                "interaction",
                timeout=120,
                check=lambda interaction: (
                    interaction.type == discord.InteractionType.component
                    and ctx.message == random_char_msg
                    and interaction.user == ctx.author,
                ),
            )
        except asyncio.TimeoutError:
            # Handle timeout by disabling buttons and updating the message content
            await randomview.on_timeout()
            await random_char_msg.edit(content="Selection timed out", view=randomview)
    except Exception as e:
        # Handle any exceptions that occur during the execution of the command
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="stats", description="Display character stats. E.g. /stats bob"
)
async def stats(ctx, *, name: str):
    """
    Display character stats.

    Args:
        ctx: The context object representing the invocation context.
        name (str): The name of the character.
    """
    try:
        # name = name.lower()

        # Define a wrapper function to pass arguments to display_character_stats
        async def display_character_stats_wrapper(
            ctx, char_name=name, server_id=ctx.guild.id
        ):
            await Character.display_character_stats(ctx, char_name, server_id)

        # Call the wrapper function to display character stats
        await display_character_stats_wrapper(ctx)
    except FileNotFoundError:
        await ctx.send(f"'{name}' savefile not found.", ephemeral=True, delete_after=15)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="lvl",
    description="Increase your Hp and get an ability score improvement if applicable. E.g. /lvl bob",
)
async def lvl(
    ctx: discord.Interaction,
    *,
    name,
):
    """
    Increases the Character's health and if applicable, grants two stat points the user can use to increase stats of their choosing.

    Args:
    - ctx (commands.Context): The context of the command.
    - name (str): The name of the character to level up.

    Raises:
    - RuntimeError: If the character's savefile is not found.
    - Exception: If any other error occurs during execution.

    Returns:
    - None
    """

    try:
        # Normalize character name to lowercase
        name = name.lower()
        # Construct paths for the server and saves directories
        server_dir = f"server_{ctx.guild.id}"
        saves_dir = os.path.join("resources", "saves", server_dir)
        # Construct file path for the character's stats file
        filepath = os.path.join(saves_dir, f"{name}_stats.csv")
        # Open the character's stats file
        with open(filepath, newline="") as file:
            reader = csv.DictReader(file)
            stats = list(reader)

        # Update the character's level
        for row in stats:
            if row["Class"] and row["Level"]:
                row["Level"] = str(int(row["Level"]) + 1)
                dndclass = row["Class"]
                lvl = row["Level"]

        # Retrieve the Constitution modifier for calculating HP
        for row in stats:
            if row["Attribute"] == "Constitution":
                const_modifier = int(row["Modifier"])
                break
        else:
            # Raise an error if Constitution modifier is not found
            raise ValueError(
                "Error: Constitution modifier not found - Can't calculate HP."
            )

        # Check if the user is authorized to level up the character
        creator_id = await get_character_creator_id(name, ctx.guild.id)
        if str(ctx.author.id) != str(creator_id):
            # Send an error message if the user is not authorized
            await ctx.send(
                "You are not authorized to level up this character. :pleading_face: ",
                ephemeral=True,
                delete_after=10,
            )
            return

        # Define hit dice for each character class
        class_dice = {
            "Sorcerer": (1, 6),
            "Wizard": (1, 6),
            "Artificer": (1, 8),
            "Bard": (1, 8),
            "Cleric": (1, 8),
            "Druid": (1, 8),
            "Monk": (1, 8),
            "Rogue": (1, 8),
            "Warlock": (1, 8),
            "Fighter": (1, 10),
            "Paladin": (1, 10),
            "Ranger": (1, 10),
            "Barbarian": (1, 12),
        }

        # Create buttons for rolling HP or taking average
        hp_roll = discord.ui.Button(
            label="Roll", custom_id="rollbutton", style=discord.ButtonStyle.red
        )
        hp_avg = discord.ui.Button(
            label="Average", custom_id="avgroll", style=discord.ButtonStyle.green
        )
        # Create a view for the buttons
        hp_view = View()
        hp_view.add_item(hp_avg)
        hp_view.add_item(hp_roll)
        # Send a message asking the user how to increase HP
        hp_msg = await ctx.send(
            "How would you like to increase your HP? Roll for it using your hit dice or take the average?",
            view=hp_view,
        )
        interaction_flag = False
        # Start an indefinite loop to wait for user interactions
        while True:
            try:
                # Wait for an interaction within a timeout period
                interaction = await bot.wait_for(
                    "interaction",
                    timeout=120,
                    # Check if the interaction is a button click from the same user or another user
                    check=lambda interaction: (
                        interaction.type == discord.InteractionType.component
                        and interaction.user == ctx.author
                        or interaction.user != ctx.author
                    ),
                )
                interaction_flag = True

                # Check if the interaction is from the command invoker
                if interaction.user == ctx.author:
                    # Check if the user chose to roll for HP
                    if interaction.data.get("custom_id") == "rollbutton":
                        # Disable buttons after selection
                        for item in hp_view.children:
                            if isinstance(item, discord.ui.Button):
                                item.style = discord.ButtonStyle.grey
                                item.disabled = True
                        # Dictionary defining the dice roll ranges for each D&D class
                        new_health_values = {}
                        # Retrieve the dice roll range for the character's class
                        roll_range = class_dice.get(dndclass)
                        # Generate a random roll within the roll range
                        roll = randint(*roll_range)
                        # Edit the message to indicate the user's choice
                        await interaction.response.edit_message(
                            content=f"You chose to roll and rolled a {roll}",
                            view=hp_view,
                        )
                        # Calculate the new health by adding the roll and Constitution modifier
                        new_health = roll + const_modifier
                        # Update the health value
                        for row in stats:
                            if row["Class"] == dndclass:
                                old_health = int(row["Health"])
                                new_health_value = new_health + old_health
                                row["Health"] = new_health_value

                        # Write the updated stats data back to the CSV file
                        with open(filepath, "w", newline="") as file:
                            fieldnames = [
                                "Name",
                                "Race",
                                "Class",
                                "Attribute",
                                "Value",
                                "Modifier",
                                "CreatorID",
                                "Level",
                                "Health",
                            ]
                            writer = csv.DictWriter(file, fieldnames=fieldnames)
                            writer.writeheader()
                            # Write each row of the updated stats data to the CSV file
                            for row in stats:
                                writer.writerow(row)

                        # Conditional to check if the character is eligible for an ability score improvement(ASI)
                        if (
                            lvl in ["4", "8", "12", "16", "19"]
                            or (
                                lvl in ["4", "8", "10", "12", "16", "19"]
                                and dndclass == "Rogue"
                            )
                            or (
                                lvl in ["4", "6", "8", "12", "14", "16", "19"]
                                and dndclass == "Fighter"
                            )
                        ):
                            # Create and display a view for ability score improvements
                            view = await MyView.create(ctx, name, None)
                            msg = await view.send_message()
                        else:
                            # Display character stats after leveling up
                            stats_message = await MyView.display_character_stats_lvl(
                                ctx, name, ctx.guild.id
                            )
                            await hp_msg.edit(
                                content=f"{stats_message}You chose to roll and rolled a {roll}"
                            )

                    # Check if the user chose to take the average for HP
                    elif interaction.data.get("custom_id") == "avgroll":
                        # Disable buttons after selection
                        for item in hp_view.children:
                            if isinstance(item, discord.ui.Button):
                                item.style = discord.ButtonStyle.grey
                                item.disabled = True
                        # Edit the message to indicate the user's choice
                        await interaction.response.edit_message(
                            content="You chose to take the average", view=hp_view
                        )
                        # Initialize an empty dictionary to store new health values
                        new_health_values = {}
                        # Retrieve the dice roll range for the character's class
                        avg_range = class_dice.get(dndclass)
                        # Calculate the average health value to add based on the class's hit dice
                        average_to_add = math.ceil(sum(avg_range) / len(avg_range))
                        new_avg_health = average_to_add + const_modifier
                        # Iterate through each row in the stats data
                        for row in stats:
                            # Retrieve the old health value from the current row
                            old_health = int(row["Health"])
                            # Calculate the new health value by adding the new average health gain and old health
                            new_health_values[row["Class"]] = (
                                new_avg_health + old_health
                            )
                        # Update the health value for each row
                        for row in stats:
                            row["Health"] = new_health_values[row["Class"]]
                        # Write the updated stats data back to the CSV file
                        with open(filepath, "w", newline="") as file:
                            fieldnames = [
                                "Name",
                                "Race",
                                "Class",
                                "Attribute",
                                "Value",
                                "Modifier",
                                "CreatorID",
                                "Level",
                                "Health",
                            ]
                            writer = csv.DictWriter(file, fieldnames=fieldnames)
                            writer.writeheader()
                            # Write each row of the updated stats data to the CSV file
                            for row in stats:
                                writer.writerow(row)
                        # Check if the character is eligible for an ability score improvement(ASI)
                        if (
                            lvl in ["4", "8", "12", "16", "19"]
                            or (
                                lvl in ["4", "8", "10", "12", "16", "19"]
                                and dndclass == "Rogue"
                            )
                            or (
                                lvl in ["4", "6", "8", "12", "14", "16", "19"]
                                and dndclass == "Fighter"
                            )
                        ):
                            # If eligible, prepare to display ASI options
                            stats_message = None
                            # Create an instance of MyView and send the message with the view
                            view = await MyView.create(ctx, name, stats_message)
                            msg = await view.send_message()
                        else:
                            # If not eligible, display character stats after leveling up
                            stats_message = await MyView.display_character_stats_lvl(
                                ctx, name, ctx.guild.id
                            )
                            await hp_msg.edit(
                                content=f"{stats_message}You chose to take the average"
                            )
                else:
                    await interaction.response.send_message(
                        "You can't do that :thinking:", ephemeral=True, delete_after=15
                    )
                    continue
                if interaction_flag:
                    break
            except asyncio.TimeoutError:
                if interaction_flag:
                    break
                else:
                    for item in hp_view.children:
                        if isinstance(item, discord.ui.Button):
                            item.style = discord.ButtonStyle.grey
                            item.disabled = True
                    await hp_msg.edit(content="Selection timed out.", view=hp_view)
    except FileNotFoundError:
        # Send an error message if the character's savefile is not found
        await ctx.send(f"'{name}' savefile not found.", ephemeral=True, delete_after=15)
    except Exception as e:
        # Send an error message if any other exception occurs
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="showall", description="Display all saved characters for the server."
)
async def showall(ctx):
    """
    Display all saved characters for the server.

    Args:
        ctx (discord.ext.commands.Context): The context object representing the invocation context.
    """
    try:
        # Construct directory path based on server ID
        server_dir = f"server_{ctx.guild.id}"
        saves_dir = os.path.join("resources", "saves", server_dir)
        # Get a list of files in the server directory
        files = os.listdir(saves_dir)
        # Extract character names from filenames
        char_info = []
        for filename in files:
            # Open each file in the server directory
            with open(os.path.join(saves_dir, filename), newline="") as file:
                # Create a CSV DictReader to read the file
                reader = csv.DictReader(file)
                try:
                    first_row = next(reader)  # Read the first row
                    second_row = next(reader)  # Read the second row
                except StopIteration:
                    continue  # Skip files with fewer than two rows

                # Get the race from the first row of the file
                race = first_row.get("Race", "")
                class_name = first_row.get("Class", "")
                # Extract character name from the filename
                char_name = filename.split("_stats.csv")[0]
                char_lvl = first_row.get("Level", "")
                # Append character name and race to the char_info list
                char_info.append((char_name, race, class_name, char_lvl))
        # Check if char_info is empty
        if not char_info:
            # Send message if no characters are found
            await ctx.send("No characters found", ephemeral=True, delete_after=30)
        else:
            # Create a formatted list of character names and races
            char_list = "\n".join(
                [
                    f"• `Name`: {name}  `Race`: {race}  `Class`: {class_name}  `Level`: {char_lvl}"
                    for name, race, class_name, char_lvl in char_info
                ]
            )
            # Send message with list of saved characters
            await ctx.send(f"**`Saved characters`**:\n{char_list}")
    except FileNotFoundError:
        # Send message if no saves are found
        await ctx.send("No saves yet")
    except Exception as e:
        # Send an error message if an exception occurs
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="rm", description="Remove saved character stats file. E.g. /rm bob"
)
async def rm(ctx, *, name: str):
    """
    Command to remove a saved character stats file.

    Args:
        ctx (discord.Context): The context of the command.
        name (str): The name of the character whose stats file is to be removed.
    """
    try:
        name = name.lower()  # Convert the character name to lowercase
        creator_id = await get_character_creator_id(name, ctx.guild.id)
        if (
            ctx.author.id != creator_id
            and not ctx.author.guild_permissions.administrator
        ):
            # Send an error message if the user is not authorized
            await ctx.send(
                "Either you are not authorized to delete this character or the savefile is corrupt. :pleading_face:\n If this was yours, contact an admin. They will be able to remove it",
                ephemeral=True,
                delete_after=20,
            )
            return
        view = RView(ctx, name)  # Create an instance of RView
        server_dir = f"server_{ctx.guild.id}"  # Construct server directory name
        saves_dir = os.path.join("resources", "saves", server_dir)
        filename = f"{name}_stats.csv"  # Construct filename
        filepath = os.path.join(saves_dir, filename)  # Construct full filepath
        if not os.path.isfile(filepath):  # Check if file exists
            await ctx.send(
                f"'{name}' savefile not found.", ephemeral=True, delete_after=20
            )  # Send error message if file doesn't exist
            return
        conf_msg = await ctx.send(  # Send confirmation message with the view
            f"Are you sure you want to delete the savefile of '{name}'? :cry:",
            view=view,
        )
        view.conf_msg = conf_msg  # Attach the confirmation message to the view
        try:
            interaction = await bot.wait_for(  # Wait for user response
                "button_click",
                timeout=60,
                check=lambda interaction: interaction.message == conf_msg
                and interaction.user == ctx.author,
            )
        except asyncio.TimeoutError:  # If timeout occurs
            # Disable buttons and edit message to indicate timeout
            await view.disable_buttons()
            await conf_msg.edit(
                content="Deletion canceled due to timeout.", view=view, delete_after=120
            )
    except Exception as e:
        # Catch any exceptions and send an error message
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="random", description="Roll a random number. E.g /random 1-100 or /random 69."
)
async def random(ctx, *, number):
    """
    Generates a random number within a specified range or up to a specified number.

    Args:
        ctx (discord.Context): The context object for the command.
        number (str): Input provided by the user in the format "<min>-<max>" or "<max>".

    Returns:
        None
    """
    # Regular expression pattern to match the input format
    pattern = r"(\d+)(-)?(\d+)?"
    match = re.match(pattern, number)

    if match:
        # Extract the first number from the input
        x = int(match.group(1))

        # Check if the first number is positive
        if x <= 0:
            await ctx.send(
                "Please enter a positive number", ephemeral=True, delete_after=20
            )
            return

        # If the input contains a range (e.g., "min-max")
        if match.group(2):
            # Extract the second number from the input
            y = int(match.group(3))

            # Check if the second number is positive and greater than or equal to the first number
            if y <= 0 or y < x:
                await ctx.send(
                    "Please enter a positive number that's equal or greater than the first number.",
                    ephemeral=True,
                    delete_after=20,
                )
                return

            # Generate a random integer within the specified range
            random_int = randint(x, y)
            await ctx.send(f"{random_int}")
        else:
            # If the input contains only one number, generate a random integer up to that number
            random_int = randint(1, x)
            await ctx.send(f"{random_int}")
    else:
        # If the input format is invalid, send an error message
        await ctx.send(
            "Invalid input. Please use '/random <number>' or '/random <min>-<max>' and use only positive numbers.",
            ephemeral=True,
            delete_after=20,
        )


@bot.hybrid_command(name="coinflip", description="Flip a coin!")
async def coinflip(ctx):
    """
    Flips a coin.

    Args:
        ctx (discord.Context): The context object for the command.

    Returns:
        None
    """
    try:
        coin = choice(
            ["Heads", "Tails"]
        )  # Using random.choice to return either Heads or Tails
        await ctx.send(
            "Flipping a coin..."
        )  # Sending a message first so that the acitivity or command doesn't time out

        # Get the current directory of the script
        current_directory = os.path.dirname(os.path.realpath(__file__))
        # Construct the full path to the GIF file
        gif_path = os.path.join(current_directory, "resources", "coin-flip.gif")

        await ctx.channel.send(
            file=discord.File(gif_path)
        )  # Sending a gif of a coinflip
        await asyncio.sleep(
            1.45
        )  # Wait for the gif to loop roughly once before displaying the result
        await ctx.channel.send(f"{coin}!")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


# Command to set a custom prefix for the bot commands
@bot.hybrid_command(
    name="setprefix",
    description="Set a custom prefix for commands - Needs admin permissions.",
)
@commands.has_permissions(administrator=True)
async def setprefix(ctx, prefix: str):
    """
    Sets a custom prefix for the bot commands in the server.

    Args:
        ctx (discord.ext.commands.Context): The context of the command.
        prefix (str): The custom prefix to set.

    Raises:
        Exception: If an error occurs during the process.

    Returns:
        None
    """
    existing_prefixes = {}
    prefixes_file = "prefixes.csv"
    prefix_folder = "resources"
    prefixes_file_path = os.path.join(prefix_folder, prefixes_file)

    # Create the prefix folder if it doesn't exist
    if not os.path.exists(prefix_folder):
        os.makedirs(prefix_folder)

    try:
        # Check if the prefixes file exists
        if os.path.exists(prefixes_file_path):
            # Read existing prefixes from the CSV file
            with open(prefixes_file_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_prefixes[int(row["ServerID"])] = row["Prefix"]

        # Set the custom prefix for the current server
        existing_prefixes[ctx.guild.id] = prefix

        # Write the updated prefixes to the CSV file
        with open(prefixes_file_path, "w", newline="") as file:
            fieldnames = ["ServerID", "Prefix"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for server_id, new_prefix in existing_prefixes.items():
                writer.writerow({"ServerID": int(server_id), "Prefix": new_prefix})

        # Send confirmation message
        await ctx.send(f"Custom prefix set to '{prefix}'.")

    except Exception as e:
        # Send error message if an exception occurs
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


# Command to remove the custom prefix
@bot.hybrid_command(
    name="rmprefix", description="Removes the custom prefix - Needs admin permissions."
)
@commands.has_permissions(administrator=True)
async def rmprefix(ctx):
    """
    Removes the custom prefix for the bot commands in the server.

    Args:
        ctx (discord.ext.commands.Context): The context of the command.

    Returns:
        None
    """
    prefixes_file = "prefixes.csv"
    prefix_folder = "resources"
    prefixes_file_path = os.path.join(prefix_folder, prefixes_file)

    # Check if the prefixes file exists
    if not os.path.exists(prefixes_file_path):
        # Send error message if the file doesn't exist
        await ctx.send("Prefix-savefile not found", ephemeral=True)
        return

    existing_prefixes = {}

    # Read existing prefixes from the CSV file
    with open(prefixes_file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_prefixes[int(row["ServerID"])] = row["Prefix"]

    # Check if the current server has a custom prefix
    if ctx.guild.id not in existing_prefixes:
        # Send error message if the prefix doesn't exist for the server
        await ctx.send("Prefix not found", ephemeral=True)
        return

    # Remove the custom prefix for the current server
    existing_prefixes.pop(ctx.guild.id)

    # Write the updated prefixes to the CSV file
    with open(prefixes_file_path, "w", newline="") as file:
        fieldnames = ["ServerID", "Prefix"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for server_id, prefix in existing_prefixes.items():
            writer.writerow({"ServerID": server_id, "Prefix": prefix})

    # Send confirmation message
    await ctx.send("Custom prefix removed")


# manually sync all global commands if necessary
@bot.command(description="sync all global commands")
@commands.is_owner()
async def syncslash(ctx):
    if ctx.author.id == 150721477480546304:
        try:
            await bot.tree.sync()
            await ctx.bot.tree.sync()
            print("Synced")
        except discord.Forbidden:
            await ctx.send("Unexpected forbidden from application scope.")
    else:
        await ctx.send("You must be the owner to use this command")


bot.run(TOKEN, log_handler=handler)
