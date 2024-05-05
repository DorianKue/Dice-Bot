import discord
from discord import (
    Intents,
    Client,
)  # Import necessary modules from Discord API
from discord.ext import commands  # Import commands extension
import random  # Import random module for generating random numbers
from dotenv import (
    load_dotenv,
)  # Import load_dotenv function to load environment variables
import os  # Import os module for interacting with the operating system
import csv  # Import csv module for working with CSV files
import asyncio  # Import asyncio module for asynchronous programming
import re  # Import re module to use regular expressions
from character import Character  # Import the Character class from character.py
from lvl_buttons import MyView
from help import CustomHelpCommand


def bot_setup():
    # Load environment variables from the .env file
    load_dotenv()

    # Get Discord token from environment variable
    TOKEN = os.getenv("DISCORD_TOKEN")

    # Create Discord bot instance with specified intents
    intents = Intents.default()
    intents.message_content = True
    bot = commands.Bot(
        command_prefix=["/"],  # Define the prefix for command invocation
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
    filepath = os.path.join(server_dir, f"{char_name}_stats.csv")

    # Check if the character's stats file exists
    if not os.path.isfile(filepath):
        return None

    # Load the creator ID from the CSV file
    with open(filepath, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Name"] == char_name:
                creator_id = int(row.get("CreatorID", 0))
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


@bot.hybrid_command(name="help", description="Shows all available commands.")
async def help(ctx):
    try:
        help_embed = await custom_help_command.send_bot_help(ctx, None)
        await ctx.send(embed=help_embed, ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="roll",
    description="Roll a specified number of dice with a specified number of sides and an optional modifier.",
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
            await ctx.send("Please specify a positive number of dice.", ephemeral=True)
            return

        # Roll the dice and calculate the total
        rolls = [random.randint(1, sides) for _ in range(num_dice)]  # Roll the dice
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
        )


@bot.hybrid_command(
    name="roll_char",
    description="Create a character using dice rolls. Excludes the lowest roll! E.g. /roll_char 4d6 bob",
)
async def roll(ctx, roll_input: str, character_name: str):
    """
    Roll stats for a character.

    Args:
        ctx (discord.ext.commands.Context): The context object representing the invocation context.
        roll_input (str): The input specifying the number of dice and sides for rolling character stats.
        character_name (str): The name of the character to be created.
    """
    try:
        # Parse input to get number of dice and sides
        num_dice, sides = map(int, roll_input.split("d"))
    except ValueError:
        # Handle invalid input format
        await ctx.send(
            "Invalid input format. Please use the format 'XdY', where X is the number of dice and Y is the number of sides.",
            ephemeral=True,
        )
        return

    # Check if the number of dice is positive
    if num_dice <= 0:
        await ctx.send(
            "Please specify a positive number of dice.",
            ephemeral=True,
        )
        return

    # Check if the character name already exists
    if os.path.isfile(f"server_{ctx.guild.id}/{character_name}_stats.csv"):
        await ctx.send(
            f"Character with name '{character_name}' already exists. Please choose a different name.",
            ephemeral=True,
        )
        return

    # Create character object and roll stats
    player = Character(character_name, ctx.guild.id)
    player.roll_stats(num_dice, sides)

    # Show stats
    await ctx.send(player.show_stats(ctx))

    # Prompt for reroll
    await ctx.channel.send("Would you like to reroll? (yes/no)")
    try:
        # Wait for the user's response to decide whether to reroll
        response = await bot.wait_for(
            "message", timeout=60, check=lambda message: message.author == ctx.author
        )
        reroll_choice = response.content.strip().lower()
        if reroll_choice in ["yes", "y"]:
            # Reroll if the user chooses to do so
            player.roll_stats(num_dice, sides)
            await ctx.channel.send(player.show_stats(ctx))
    except asyncio.TimeoutError:
        # Handle timeout if the user doesn't respond to the reroll prompt
        await ctx.send("Timed out. Reroll canceled.", ephemeral=True)
        return

    # Save character stats to CSV
    await player.save_to_csv(character_name, ctx)


@bot.hybrid_command(
    name="stats", description="Display character stats. E.g. /stats Bob"
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
        await ctx.send(f"'{name}' savefile not found.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="lvl",
    description="Add 2 stat points of your choosing to your character. E.g. /lvl Bob",
)
async def lvl(ctx, *, name):
    try:
        name = name.lower()
        # Check if the user is the creator of the character or has admin permissions
        creator_id = await get_character_creator_id(name, ctx.guild.id)
        if (
            ctx.author.id != creator_id
            and not ctx.author.guild_permissions.administrator
        ):
            await ctx.send(
                "You are not authorized to level up this character.", ephemeral=True
            )
            return
        # Retrieve the stats table message if it already exists
        stats_message = None
        async for message in ctx.channel.history(limit=3):
            if message.author == ctx.guild.me and message.embeds:
                if "Character's Stats" in message.embeds[0].title:
                    stats_message = message
                    break
        # Create an instance of MyView and send the message with the view
        view = await MyView.create(ctx, name, stats_message)
        await view.send_message()

    except RuntimeError:
        await ctx.send(f"'{name}' savefile not found.", ephemeral=True)
    except Exception as e:
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
        char_names = [filename.split("_stats.csv")[0] for filename in files]
        # Format the character names with bullet points and new lines
        char_list = "\n".join([f"• {name}" for name in char_names])
        # Send the list of character names as a message
        if len(char_list) == 0:
            await ctx.send("No characters found")
        else:
            await ctx.send(f"**`Saved characters`**:\n{char_list}")
    except FileNotFoundError:
        await ctx.send("No saves yet")
    except Exception as e:
        # Send an error message if an exception occurs
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="rm", description="Remove saved character stats file. E.g. /rm bob"
)
async def rm(ctx, *, name: str):
    """
    Remove character stats file if the user has appropriate permissions.

    Args:
        ctx (Context): The context object representing the invocation context.
        name (str): The name of the character whose stats file needs to be removed.
    """
    try:
        name = name.lower()
        # Construct filepath for the character's stats file
        server_dir = f"server_{ctx.guild.id}"  # Construct server directory name based on guild ID
        filename = f"{name}_stats.csv"  # Construct filename based on character name
        filepath = os.path.join(
            server_dir, filename
        )  # Combine server directory and filename to get full filepath

        # Check if the character's stats file exists
        if not os.path.isfile(filepath):  # Check if filepath points to a file
            await ctx.send(
                f"'{name}' savefile not found.", ephemeral=True
            )  # Send error message if file doesn't exist
            return

        # Load the user ID who created the character from the CSV file
        with open(filepath, newline="") as file:  # Open the character's stats file
            reader = csv.DictReader(file)  # Create a CSV DictReader object
            creator_id = None
            for row in reader:  # Iterate through each row in the CSV
                if (
                    row["Name"].lower() == name
                ):  # Check if the row corresponds to the character name
                    creator_id = int(
                        row.get("CreatorID", 0)
                    )  # Get the ID of the creator from the CSV
                    break  # Stop iterating if the character is found

            if creator_id is None:
                # Check if the user is allowed to access the directory
                if not os.access(server_dir, os.R_OK):
                    await ctx.send(
                        f"Unable to access '{name}' savefile.",
                        ephemeral=True,
                    )  # Send error message if access is denied
                    return

                await ctx.send(
                    f"Unable to determine creator of character '{name}'.",
                    ephemeral=True,
                )  # Send error message if creator ID not found
                return

        # Check if the user is the creator of the character or has admin permissions
        if (
            ctx.author.id == creator_id or ctx.author.guild_permissions.administrator
        ):  # Check user permissions
            # Prompt for confirmation before deletion
            await ctx.send(
                f"Are you sure you want to delete the savefile of '{name}'? (y/n)"
            )
            response = await bot.wait_for(  # Wait for user response
                "message",
                timeout=60,
                check=lambda message: message.author == ctx.author
                and message.content.lower() in ["y", "yes", "no", "n"],
            )
            # Delete file if confirmed by the user
            if response.content.lower() in ["y", "yes"]:  # Check user confirmation
                os.remove(filepath)  # Delete the character's stats file
                await ctx.channel.send(
                    f"File '{filename}' deleted successfully."
                )  # Send success message
            else:
                await ctx.send(
                    "Deletion canceled", ephemeral=True
                )  # Send cancellation message if user cancels
        else:
            await ctx.send(
                "You are not authorized to delete this character.", ephemeral=True
            )  # Send error message if user lacks permissions
    except asyncio.TimeoutError:  # Handle timeout exception
        await ctx.send(
            "Timed out. Deletion canceled.", ephemeral=True
        )  # Send message if deletion times out
    except Exception as e:  # Handle other exceptions
        await ctx.send(
            f"An error occurred: {e}", ephemeral=True
        )  # Send error message if other exception occurs


@bot.hybrid_command(name="wrist", description="Big sad :(")
async def wrist(ctx):
    try:
        name = ctx.message.author.display_name
        await ctx.send(f"R.I.P {name}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


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
