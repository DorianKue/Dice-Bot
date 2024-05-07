import discord  # Import the discord module
from discord.ext import commands  # Import the commands module from discord.ext
from character import Character  # Import the Character class from character.py
from yn_buttons import YView  # Import the YView class from yn_buttons.py
import asyncio  # Import the asyncio module for handling asynchronous operations
from discord import Intents  # Import the Intents class from discord module

# Initialize the bot with specified parameters
bot = commands.Bot(
    command_prefix=["/"],  # Define the prefix for command invocation
    intents=Intents.default(),  # Enable the default intents
    help_command=None,  # Disable the default help command
    case_insensitive=True,  # Enable case insensitivity for commands
)


class RCView(discord.ui.View):
    """
    View class for race selection during character creation.
    """

    class RaceButton(discord.ui.Button):
        """
        Button subclass representing race selection buttons.

        Attributes:
            race (str): The race associated with the button.
            label (str): The label displayed on the button.
            view (RCView): The parent view.
            ctx (discord.Interaction): The context of the command.
            num_dice (int): Number of dice for rolling stats.
            sides (int): Number of sides for rolling stats.
            race_name (str): The name of the selected race.
        """

        def __init__(self, race, label, view, ctx, num_dice, sides, race_name):
            """
            Initialize the RaceButton.

            Args:
                race (str): The race associated with the button.
                label (str): The label displayed on the button.
                view (RCView): The parent view.
                ctx (discord.Interaction): The context of the command.
                num_dice (int): Number of dice for rolling stats.
                sides (int): Number of sides for rolling stats.
                race_name (str): The name of the selected race.
            """
            # Initialize attributes
            self.ctx = ctx  # Store the interaction context
            self.race = race  # Store the race associated with the button
            self._view = view  # Store the parent view
            self.num_dice = num_dice  # Store the number of dice for rolling stats
            self.sides = sides  # Store the number of sides for rolling stats
            self.race_name = race_name  # Store the name of the selected race
            # Determine button style based on race
            style = (
                discord.ButtonStyle.red  # Set button style to red for specific races
                if race in ["Dragonborn", "Tiefling", "Half-Orc", "Other"]
                else (
                    discord.ButtonStyle.green  # Set button style to green for specific races
                    if race in ["Dwarf", "Gnome", "Halfling"]
                    else discord.ButtonStyle.blurple  # Set button style to blurple for others
                )
            )
            super().__init__(
                label=label,  # Set the label displayed on the button
                style=style,  # Set the style of the button
                custom_id=race,  # Set the custom ID of the button
            )

        async def callback(self, interaction: discord.Interaction):
            """
            Callback function executed when the button is clicked.

            Args:
                interaction (discord.Interaction): The interaction object.
            """
            # Check button availability
            if self.view and not await self.view.button_check(interaction):
                return
            # Disable all buttons in the view
            await self.view.disable_buttons()
            if self.custom_id == "Other":
                # Prompt user to enter custom race
                await interaction.response.send_message(
                    content="Please enter your race:"  # Send message asking for race input
                )
                try:
                    # Wait for user's response
                    response = await self.ctx.bot.wait_for(
                        "message",
                        check=lambda m: m.author
                        == self.ctx.author  # Check if the message author is the same as the interaction user
                        and m.channel
                        == self.ctx.channel,  # Check if the message is sent in the same channel as the interaction
                        timeout=120,  # Set timeout for waiting for response
                    )
                    custom_race = (
                        response.content
                    )  # Get the content of the user's message as custom race
                    # Set custom race
                    self.custom_race = custom_race
                    # Prepare stat message and display reroll options
                    stat_msg_content, player, race_name = (
                        await self.prepare_stat_message(interaction)
                    )  # Prepare stat message content, character, and race name
                    reroll_view = YView(
                        self.ctx,
                        self._view.num_dice,
                        self._view.sides,
                        self._view.character_name,
                        player,
                        race_name,
                    )  # Create a new view for reroll options
                    await interaction.followup.send(
                        content=stat_msg_content, view=reroll_view
                    )  # Send a new follow-up message with reroll options
                except asyncio.TimeoutError:
                    await interaction.followup.send(
                        "Input timed out", ephemeral=True
                    )  # Send message indicating timeout
            else:
                # Prepare stat message and display reroll options
                stat_msg_content, player, race_name = await self.prepare_stat_message(
                    interaction
                )  # Prepare stat message content, character, and race name
                reroll_view = YView(
                    self.ctx,
                    self._view.num_dice,
                    self._view.sides,
                    self._view.character_name,
                    player,
                    race_name,
                )  # Create a new view for reroll options
                # Edit the original message to include the combined content
                await interaction.response.edit_message(
                    content=stat_msg_content, view=reroll_view
                )

        @staticmethod
        async def roll_char(
            interaction: discord.Interaction, ctx, character_name, num_dice, sides
        ):
            """
            Roll character stats and send a message with stat table and reroll options.

            Args:
                interaction (discord.Interaction): The interaction object.
                ctx (discord.Interaction): The context of the command.
                character_name (str): The name of the character.
                num_dice (int): Number of dice for rolling stats.
                sides (int): Number of sides for rolling stats.
            Returns:
                Tuple[discord.Message, Character]: The message object containing the displayed stats and the Character object.
            """
            # Create character object and roll stats
            player = Character(character_name, ctx.guild.id)
            player.roll_stats(num_dice, sides)
            # Show stats
            stats_message = await interaction.followup.send(player.show_stats(ctx))
            # Construct the Yes/No buttons view
            return stats_message, player

        async def prepare_stat_message(self, interaction):
            """
            Prepare the stat message with the stat table and reroll options.

            Args:
                interaction (discord.Interaction): The interaction object.

            Returns:
                Tuple[str, Character, str]: The message content, Character object, and race name.
            """
            # Create character object and roll stats
            player = Character(self._view.character_name, self.ctx.guild.id)
            player.roll_stats(self._view.num_dice, self._view.sides)

            # Determine the race name
            if self.race == "Other":
                race_name = self.custom_race
            else:
                race_name = self.race

            # Generate the stat table
            stats_table = player.show_stats(self.ctx, race_name)

            # Construct the Yes/No buttons view
            reroll_view = YView(
                self.ctx,
                self._view.num_dice,
                self._view.sides,
                self._view.character_name,
                player,
                race_name,
            )

            # Combine the stat table and reroll options into a single message content
            stat_msg_content = f"{stats_table}Would you like to reroll?"

            return stat_msg_content, player, race_name

        @property
        def view(self):
            """
            Get the parent view.

            Returns:
                RCView: The parent view.
            """
            return self._view

        @view.setter
        def view(self, race):
            """
            Set the parent view.

            Args:
                race (RCView): The parent view.
            """
            self._view = race

    def __init__(self, ctx, character_name, num_dice, sides, race_name):
        """
        Initialize the RCView.

        Args:
            ctx (discord.Interaction): The context of the command.
            character_name (str): The name of the character being created.
            num_dice (int): Number of dice for rolling stats.
            sides (int): Number of sides for rolling stats.
            race_name (str): The name of the selected race.
        """
        super().__init__()  # Call the constructor of the parent class
        self.num_dice = num_dice  # Store the number of dice for rolling stats
        self.sides = sides  # Store the number of sides for rolling stats
        self.ctx = ctx  # Store the interaction context
        self.character_name = character_name  # Store the character name
        self.command_invoker_id = ctx.author.id  # Store the ID of the command invoker
        self.race_name = race_name  # Store the name of the selected race

    async def add_buttons(self, race_name):
        """
        Add race selection buttons to the view.

        Args:
            race_name (str): The name of the selected race.
        """
        for race in [
            "Dragonborn",
            "Dwarf",
            "Elf",
            "Gnome",
            "Half-Elf",
            "Half-Orc",
            "Halfling",
            "Human",
            "Tiefling",
            "Other",
        ]:
            button = self.RaceButton(
                race,  # Set the race associated with the button
                race,  # Set the label displayed on the button
                self,  # Set the parent view
                self.ctx,  # Set the interaction context
                self.num_dice,  # Set the number of dice for rolling stats
                self.sides,  # Set the number of sides for rolling stats
                race_name,  # Set the name of the selected race
            )
            self.add_item(button)  # Add the button to the view

    @classmethod
    async def create(cls, ctx, race, num_dice, sides, race_name):
        """
        Create an instance of RCView.

        Args:
            ctx (discord.Interaction): The context of the command.
            race (str): The selected race.
            num_dice (int): Number of dice for rolling stats.
            sides (int): Number of sides for rolling stats.
            race_name (str): The name of the selected race.

        Returns:
            RCView: The created instance of RCView.
        """
        self = RCView(ctx, race, num_dice, sides, race_name)  # Initialize the instance
        await self.add_buttons(race_name)  # Add race selection buttons to the view
        return self

    async def disable_buttons(self):
        """
        Disable all buttons in the view.
        """
        for child in self.children:  # Iterate through all children of the view
            if isinstance(child, discord.ui.Button):  # Check if the child is a Button
                child.disabled = True  # Disable the button
                child.style = discord.ButtonStyle.gray  # Set the button style to gray

    async def on_timeout(self):
        """
        Handler for when the view times out.
        """
        await self.disable_buttons()  # Disable all buttons in the view

    async def button_check(self, interaction: discord.Interaction):
        """
        Check if the button interaction is valid.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            bool: True if the button interaction is valid, False otherwise.
        """
        if interaction.user.id != self.command_invoker_id:
            await interaction.response.send_message(
                content="This is not your decision to make. :point_up: :nerd:",  # Send error message for invalid user
                ephemeral=True,  # Make the error message ephemeral
                delete_after=10,  # Set the deletion time for the error message
            )
            return False  # Return False for invalid interaction
        return True  # Return True for valid interaction
