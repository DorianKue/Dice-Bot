import discord
from discord import (
    Intents,
)  # Import necessary modules from Discord API
from discord.ext import commands  # Import commands extension
from random import randint, choice  # Import random module for generating random numbers
from dotenv import (
    load_dotenv,
)  # Import load_dotenv function to load environment variables
import os  # Import os module for interacting with the operating system
import csv  # Import csv module for working with CSV files
import asyncio  # Import asyncio module for asynchronous programming
import re  # Import re module to use regular expressions
from character import Character  # Import the Character class from character.py
from components.lvl_buttons import MyView
from commands.help import CustomHelpCommand
from components.rm_buttons import RView
from components.racebuttons import RCView


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
    return bot, TOKEN


bot, TOKEN = bot_setup()
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
    # Construct the full file path
    filepath = os.path.join(server_dir, f"{char_name.lower()}_stats.csv")

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


async def help_cogs(ctx):
    """
    Asynchronously adds the CustomHelpCommand cog to the bot.

    This function is used to add the CustomHelpCommand cog to the bot.
    The CustomHelpCommand cog provides custom help functionality for displaying bot commands.
    This function is typically called when the bot is initialized or when the help command is invoked.

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

        # Check if the character name already exists
        if os.path.isfile(f"server_{ctx.guild.id}/{character_name}_stats.csv"):
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
    description="Add 2 stat points of your choosing to your character. E.g. /lvl bob",
)
async def lvl(
    ctx,
    *,
    name,
):
    """
    Allows the user to add 2 stat points of their choosing to a character.

    Parameters:
    - ctx (commands.Context): The context of the command.
    - name (str): The name of the character to level up.

    Raises:
    - RuntimeError: If the character's savefile is not found.
    - Exception: If any other error occurs during execution.

    Returns:
    - None

    The function first checks the authorization of the user to level up the character,
    ensuring they are either the creator of the character or have admin permissions.

    It then attempts to retrieve the latest stats message for the character.

    Next, it creates an instance of the MyView class, which handles the interactive
    button-based interface for leveling up the character.

    If the user does not interact with the buttons within 180 seconds, the function
    handles the timeout by disabling the buttons.

    If any errors occur during execution, appropriate error messages are sent.
    """
    try:
        name = name.lower()  # Normalize character name to lowercase
        server_dir = f"server_{ctx.guild.id}"
        filepath = os.path.join(server_dir, f"{name}_stats.csv")
        with open(filepath, newline="") as file:
            reader = csv.DictReader(file)
            stats = list(reader)

        for row in stats:
            if row["Attribute"] == "Constitution":
                const_modifier = int(row["Modifier"])
                break
            if row["Class"] and row["Level"]:
                row["Level"] = str(int(row["Level"]) + 1)
                dndclass = row["Class"]
                lvl = row["Level"]

        else:
            raise ValueError(
                "Error: Constitution modifier not found - Can't calculate HP."
            )

        # Check if the user is the creator of the character or has admin permissions
        creator_id = await get_character_creator_id(name, ctx.guild.id)
        if (
            ctx.author.id != creator_id
            and not ctx.author.guild_permissions.administrator
        ):
            # Send an error message if the user is not authorized
            await ctx.send(
                "You are not authorized to level up this character. :pleading_face: ",
                ephemeral=True,
                delete_after=10,
            )
            return

        # Dictionary defining the dice roll ranges for each D&D class
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

        # Dictionary to store updated health values for each class
        new_health_values = {}

        # Retrieve the Constitution modifier from the first row with "Constitution" attribute
        const_modifier = int(
            next(row for row in stats if row["Attribute"] == "Constitution")["Modifier"]
        )
        # Retrieve the character's class from the first row of the stats data
        dndclass = stats[0]["Class"]
        # Retrieve the dice roll range for the character's class
        roll_range = class_dice.get(dndclass)
        # Generate a random roll within the roll range
        roll = randint(*roll_range)
        # Calculate the new health by adding the roll and Constitution modifier
        new_health = roll + const_modifier
        print(f"ROLL: {roll} | MODIFIER: {const_modifier} NEW HEALTH: {new_health}")

        for row in stats:
            # Retrieve the old health value from the current row
            old_health = int(row["Health"])
            # Update the new health value for the current class
            new_health_values[row["Class"]] = new_health + old_health

        # Update the health value for each row based on class
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

        # Conditional to check if the character is eligible for an ability score improvement(ASI)
        if (
            lvl in ["4", "8", "12", "16", "19"]
            or (lvl in ["4", "8", "10", "12", "16", "19"] and dndclass == "Rogue")
            or (
                lvl in ["4", "6", "8", "12", "14", "16", "19"] and dndclass == "Fighter"
            )
        ):
            # Retrieve the stats table message if it already exists
            stats_message = None
            # Create an instance of MyView and send the message with the view
            view = await MyView.create(ctx, name, stats_message)
            msg = await view.send_message()
            try:
                # Wait for button click interaction within 180 seconds
                interaction = await bot.wait_for(
                    "button_click",
                    timeout=150,
                    check=lambda interaction: interaction.message == msg
                    and interaction.user == ctx.author,
                )
            # Handle timeouts and disable buttons on timeout
            except asyncio.TimeoutError:
                await view.on_timeout()
        else:
            stats_message = await MyView.display_character_stats_lvl(
                ctx, name, ctx.guild.id
            )
            await ctx.send(f"{stats_message}")

    except RuntimeError:
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
        # Get a list of files in the server directory
        files = os.listdir(server_dir)
        # Extract character names from filenames
        char_info = []
        for filename in files:
            # Open each file in the server directory
            with open(os.path.join(server_dir, filename), newline="") as file:
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
        filename = f"{name}_stats.csv"  # Construct filename
        filepath = os.path.join(server_dir, filename)  # Construct full filepath
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

    Parameters:
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

    Parameters:
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


@bot.hybrid_command(name="wrist", description="Big sad :(")
async def wrist(ctx):
    """
    Joke command because after i mentioned "slash" commands to him, he suggested to make a command called wrist lol.

    Parameters:
        ctx (discord.Context): The context object for the command.
    """
    try:
        name = ctx.message.author.display_name
        await ctx.send(f"R.I.P {name}")
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
            await ctx.bot.tree.sync(guild=ctx.guild)
            print("Synced")
        except discord.Forbidden:
            await ctx.send("Unexpected forbidden from application scope.")
    else:
        await ctx.send("You must be the owner to use this command")


bot.run(TOKEN)
