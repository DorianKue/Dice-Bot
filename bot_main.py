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

# Load environment variables from the .env file
load_dotenv()

# Get Discord token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Create Discord bot instance with specified intents
intents = Intents.default()
intents.message_content = True
client = Client(
    intents=intents
)  # Initialize a Discord client with the specified intent


class CustomHelpCommand(commands.DefaultHelpCommand):
    """Custom help command for displaying bot commands."""

    async def send_bot_help(self, mapping):
        """
        Send help message for the bot.

        Args:
            mapping (dict): Mapping of cogs to their commands.
        """
        # Create an Embed instance for formatting the help message
        embed = discord.Embed(
            title="Command Help",  # Title of the embed
            description="`Prefix`:\n"
            "You can either use `!` or `/` for commands.\n"
            "\n"
            "**`❗Important❗`**: If you use the same name as someone else when creating a character, the previous character will be overwritten for now!\n"
            "\n"
            "**Available commands:**",  # Description of the embed
            color=discord.Color.blue(),  # Color of the embed
        )

        # Add a field for lvling up
        embed.add_field(
            name="Adding stats/Lvling up:",  # Title of the field
            value=(
                "`!lvl Name` - where `Name` is the name of your character.\n"
                "Example: `!lvl bob`.\n"
                "This command allows you to add 2 stat points of your choosing to your character."
            ),  # Value for the field
            inline=False,
        )

        # Add a field for rolling dice
        embed.add_field(
            name="Rolling dice:",  # Title of the field
            value="`!roll XdY` - where X is the number of dice and Y is the sides of dice.\n"
            "Example: `!roll 4d6` to roll 4 dice with 6 sides.\n"
            "*Optionally* you can add a modifier that gets added or subtracted from the end result.\n"
            "Example: `!roll 4d6+2` or `!roll 4d6-2`",  # Value fo the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for creating a character
        embed.add_field(
            name="Create a character using dice rolls (__Excludes__ the lowest roll):",  # Title of the field
            value="`!roll_char XdY` - where X is the number of dice and Y is the sides of dice.\n"
            "Example: `!roll_char 4d6` to roll 4 dice with 6 sides.\nThe bot will ask you for your Characters name *after* the initial roll command.",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for showing created character stats
        embed.add_field(
            name="Showing created character stats:",  # Title of the field
            value="`!stats Name` - where `Name` is the name of your character. Example: `!stats bob`",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for deleting a character savefile
        embed.add_field(
            name="Remove a character stat savefile:",  # Title of the field
            value="`!rm Name` - where `Name` is the name of your character. \nExample: `!rm bob`\n"
            "Deleting a savefile is restricted to the character's creator or individuals with admin privileges.",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for showing all characters
        embed.add_field(
            name="Show all saved characters:",  # Title of the field
            value="`!showall`",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Iterate through each command and add its name and description to the embed
        for cog, commands_list in mapping.items():
            if cog:  # Check if the command belongs to a cog
                embed.add_field(
                    name=cog.qualified_name,  # Name of the cog as the title of the field
                    value="\n".join(  # Join command names and their descriptions with new lines
                        [
                            f"`{command.name}` - {command.brief or 'No description available.'}"
                            for command in commands_list
                        ]
                    ),
                    inline=False,  # Display the field in a new line
                )

        # Send the embed
        await self.get_destination().send(embed=embed)


bot = commands.Bot(
    command_prefix=["!", "/"],
    intents=intents,
    help_command=CustomHelpCommand(),
    case_insensitive=True,
)


@bot.event
async def on_ready():
    """Print a message when the bot is ready."""
    print("Bot is ready.")


@bot.event
async def on_message(message):
    """Process incoming messages."""
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
        await ctx.send(f"An error occurred: {error}")


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


@bot.command()
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
        await ctx.send(f"An error occurred: {e}")


@bot.command()
async def lvl(ctx, *, char_name):
    try:
        # char_name = char_name.lower()

        # Check if the user is the creator of the character or has admin permissions
        creator_id = await get_character_creator_id(char_name, ctx.guild.id)
        if (
            ctx.author.id != creator_id
            and not ctx.author.guild_permissions.administrator
        ):
            await ctx.send(
                "You are not authorized to level up this character.", ephemeral=True
            )
            return

        # Retrieve the stats message if it already exists
        stats_message = None  # Initialize stats_message
        # Retrieve stats message by searching through the channel's history
        async for message in ctx.channel.history(limit=2):
            if message.author == ctx.guild.me and message.embeds:
                # Assuming the stats table is sent as an embed
                if "Character's Stats" in message.embeds[0].title:
                    stats_message = message
                    break

        # Display character stats and update the existing stats message if available
        stats_message = await Character.display_character_stats_lvl(
            ctx, char_name, ctx.guild.id, stats_message
        )

        # Create an instance of MyView and send the message with the view
        view = MyView(ctx, char_name, stats_message)
        buttons_message = await ctx.send(
            "Select which attribute you want to increase:", view=view
        )

        # Update the MyView instance with the buttons message
        view.message = buttons_message

    except RuntimeError:
        await ctx.send(f"'{char_name}' savefile not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


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


@bot.command(name="roll")
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
            await ctx.send("Please specify a positive number of dice.")
            return

        # Roll the dice and calculate the total
        rolls = [random.randint(1, sides) for _ in range(num_dice)]  # Roll the dice
        total = sum(rolls) + modifier  # Calculate the total by adding the modifier

        # Send the roll results to the channel
        if num_dice > 1:
            await ctx.send(
                f"You rolled: {rolls}\nTotal: {total}"
            )  # Send rolls and total
        else:
            await ctx.send(f"You rolled: {rolls}")  # Send rolls only if one die rolled
    else:
        # Send error message for invalid input format
        await ctx.send(
            "Invalid input format. Please use the format 'XdY' or 'XdY+/-Z', where X is the number of dice, Y is the number of sides, and Z is the modifier."
        )


@bot.command(name="roll_char")
async def roll(ctx, *, roll_input: str):
    """
    Roll stats for a character.

    Args:
        ctx: The context object representing the invocation context.
        roll_input (str): The input specifying the number of dice and sides for rolling character stats.
    """
    try:
        # Parse input to get number of dice and sides
        num_dice, sides = map(int, roll_input.split("d"))
    except ValueError:
        # Handle invalid input format
        await ctx.send(
            "Invalid input format. Please use the format 'XdY', where X is the number of dice and Y is the number of sides."
        )
        return

    # Check if the number of dice is positive
    if num_dice <= 0:
        await ctx.send("Please specify a positive number of dice.")
        return

    # Prompt for character name
    await ctx.send("What's the name of your character?")
    try:
        # Wait for the user's response to get the character name
        response = await bot.wait_for(
            "message", timeout=60, check=lambda message: message.author == ctx.author
        )
        character_name = response.content.strip()
    except asyncio.TimeoutError:
        # Handle timeout if the user doesn't provide a character name
        await ctx.send("Timed out. Character name not provided.")
        return

    # Create character object and roll stats
    player = Character(character_name, ctx.guild.id)
    player.roll_stats(num_dice, sides)

    # Show stats
    await player.show_stats(ctx)

    # Prompt for reroll
    await ctx.send("Would you like to reroll? (yes/no)")
    try:
        # Wait for the user's response to decide whether to reroll
        response = await bot.wait_for(
            "message", timeout=60, check=lambda message: message.author == ctx.author
        )
        reroll_choice = response.content.strip().lower()
        if reroll_choice in ["yes", "y"]:
            # Reroll if the user chooses to do so
            player.roll_stats(num_dice, sides)
            await player.show_stats(ctx)
    except asyncio.TimeoutError:
        # Handle timeout if the user doesn't respond to the reroll prompt
        await ctx.send("Timed out. Reroll canceled.")
        return

    # Save character stats to CSV
    await player.save_to_csv(character_name, ctx)


@bot.command()
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
        await ctx.send(f"'{name}' savefile not found.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command()
async def rm(ctx, *, name: str):
    """
    Remove character stats file if the user has appropriate permissions.

    Args:
        ctx (Context): The context object representing the invocation context.
        name (str): The name of the character whose stats file needs to be removed.
    """
    try:
        # name = name.lower()
        # Construct filepath for the character's stats file
        server_dir = f"server_{ctx.guild.id}"  # Construct server directory name based on guild ID
        filename = f"{name}_stats.csv"  # Construct filename based on character name
        filepath = os.path.join(
            server_dir, filename
        )  # Combine server directory and filename to get full filepath

        # Check if the character's stats file exists
        if not os.path.isfile(filepath):  # Check if filepath points to a file
            await ctx.send(
                f"'{name}' savefile not found."
            )  # Send error message if file doesn't exist
            return

        # Load the user ID who created the character from the CSV file
        with open(filepath, newline="") as file:  # Open the character's stats file
            reader = csv.DictReader(file)  # Create a CSV DictReader object
            for row in reader:  # Iterate through each row in the CSV
                if (
                    row["Name"] == name
                ):  # Check if the row corresponds to the character name
                    creator_id = int(
                        row.get("CreatorID", 0)
                    )  # Get the ID of the creator from the CSV
                    break  # Stop iterating if the character is found
            else:
                await ctx.send(
                    f"Unable to determine creator of character '{name}'."
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
                await ctx.send(
                    f"File '{filename}' deleted successfully."
                )  # Send success message
            else:
                await ctx.send(
                    "Deletion canceled"
                )  # Send cancellation message if user cancels
        else:
            await ctx.send(
                "You are not authorized to delete this character."
            )  # Send error message if user lacks permissions
    except asyncio.TimeoutError:  # Handle timeout exception
        await ctx.send(
            "Timed out. Deletion canceled."
        )  # Send message if deletion times out
    except RuntimeError:
        await ctx.send(f"'{name}' savefile not found.")
    except Exception as e:  # Handle other exceptions
        await ctx.send(
            f"An error occurred: {e}"
        )  # Send error message if other exception occurs


bot.run(TOKEN)
