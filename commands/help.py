import discord
from discord.ext import commands


class CustomHelpCommand(commands.Cog):
    """Custom help command for displaying bot commands."""

    def __init__(self, bot):
        self.bot = bot

    async def send_bot_help(self, ctx, mapping):
        """
        Send help message for the bot.

        Args:
            mapping (dict): Mapping of cogs to their commands.
        """
        # Create an Embed instance for formatting the help message
        embed = discord.Embed(
            title="Command Help",  # Title of the embed
            description="`Prefix`:\n"
            "This Bot uses '`/`' as a prefix\n"
            "However you can set a custom prefix using /setprefix `insert custom prefix`. E.g. `/setprefix !`\n"
            "Now you can use your custom prefix together with slash commands."
            "\n"
            "\n"
            "**Available commands:**",  # Description of the embed
            color=discord.Color.blue(),  # Color of the embed
        )

        # Add a field for rolling dice
        embed.add_field(
            name="Rolling dice:",  # Title of the field
            value="`/roll XdY` - where X is the number of dice and Y is the sides of dice.\n"
            "Example: `/roll 4d6` to roll 4 dice with 6 sides.\n"
            "*Optionally* you can add a modifier that gets added or subtracted from the end result.\n"
            "Example: `/roll 4d6+2` or `/roll 4d6-2`",  # Value fo the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for creating a character
        embed.add_field(
            name="Create a character using dice rolls (__Excludes__ the lowest roll):",  # Title of the field
            value="`/roll_char XdY Name` - where X is the number of dice, Y is the sides of dice and Name is the name of your Character.\n"
            "Example: `/roll_char 4d6 bob` to roll 4 dice with 6 sides.",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for showing created character stats
        embed.add_field(
            name="Showing created character stats:",  # Title of the field
            value="`/stats Name` - where `Name` is the name of your character. Example: `/stats bob`",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for lvling up
        embed.add_field(
            name="Adding stats/Lvling up:",  # Title of the field
            value=(
                "`/lvl Name` - where `Name` is the name of your character.\n"
                "Example: `/lvl bob`.\n"
                "Levels up your character and increases their health. This command also allows you to add 2 stat points of your choosing to your character, if eligible for an ASI."
            ),  # Value for the field
            inline=False,
        )

        # Add a field for showing all characters
        embed.add_field(
            name="Show all saved characters:",  # Title of the field
            value="`/showall`",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for deleting a character savefile
        embed.add_field(
            name="Remove a character stat savefile:",  # Title of the field
            value="`/rm Name` - where `Name` is the name of your character. \nExample: `/rm bob`\n"
            "Deleting a savefile is restricted to the character's creator or individuals with admin privileges.",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for random command
        embed.add_field(
            name="Roll a random number:",  # Title of the field
            value="`/random X` - To roll a number between 1 and `X` where X has to be a positive number. \nExample: `/random 100`\n"
            "You can also use `/random X-Y` - To roll a number between `X` and `Y` where X and Y have to be a positive number. \n Example: `/random 69-100`\n",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Add a field for coinflip command
        embed.add_field(
            name="A coinflip:",  # Title of the field
            value="`/coinflip` - That's it. It flips a coin and returns Heads or Tails",  # Value of the field
            inline=False,  # Display the field in a new line
        )

        # Iterate through each command and add its name and description to the embed
        for cog, commands_list in self.bot.cogs.items():
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

        # Return the embed
        return embed
