import discord
from discord import (
    Intents,
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
from yn_buttons import YView
from rm_buttons import RView


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
            await ctx.send(
                "Please specify a positive number of dice.",
                ephemeral=True,
                delete_after=10,
            )
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

        # Create character object and roll stats
        player = Character(character_name, ctx.guild.id)
        player.roll_stats(num_dice, sides)
        # Show stats
        await ctx.send(player.show_stats(ctx))

        # Construct the Yes/No buttons view
        view = YView(ctx, num_dice, sides, character_name)
        reroll_message = await ctx.channel.send("Would you like to reroll?", view=view)
        view.reroll_message = reroll_message

        try:
            # Wait for button click interaction
            interaction = await bot.wait_for(
                "button_click",
                timeout=120,
                check=lambda interaction: interaction.message == reroll_message
                and interaction.user == ctx.author,
            )
            view = YView(ctx, num_dice, sides, character_name)

        except asyncio.TimeoutError:
            # If timeout occurs, disable buttons and edit message
            await view.disable_buttons()
            await reroll_message.edit(
                content="Reroll timed out. Character stats have been saved.",
                view=view,
                delete_after=120,
            )
            await player.save_to_csv(character_name, ctx)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


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
        await ctx.send(f"'{name}' savefile not found.", ephemeral=True, delete_after=15)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)


@bot.hybrid_command(
    name="lvl",
    description="Add 2 stat points of your choosing to your character.",
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
        # Retrieve the stats table message if it already exists
        stats_message = None
        async for message in ctx.channel.history(limit=3):
            if message.author == ctx.guild.me and message.embeds:
                if "Character's Stats" in message.embeds[0].title:
                    stats_message = message
                    break
        # Create an instance of MyView and send the message with the view
        view = await MyView.create(ctx, name, stats_message)
        msg = await view.send_message()
        try:
            # Wait for button click interaction within 180 seconds
            interaction = await bot.wait_for(
                "button_click",
                timeout=180,
                check=lambda interaction: interaction.message == msg
                and interaction.user == ctx.author,
            )
        # Handle timeouts and disable buttons on timeout
        except asyncio.TimeoutError:
            await view.on_timeout()
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
        char_names = [filename.split("_stats.csv")[0] for filename in files]
        # Format the character names with bullet points and new lines
        char_list = "\n".join([f"• {name}" for name in char_names])
        # Send the list of character names as a message
        if len(char_list) == 0:
            await ctx.send("No characters found", ephemeral=True, delete_after=30)
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
                "You are not authorized to delete this character. :pleading_face:",
                ephemeral=True,
                delete_after=10,
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
