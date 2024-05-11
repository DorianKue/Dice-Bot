import discord  # Import the discord module
from discord.ext import commands  # Import the commands module from discord.ext
import asyncio  # Import the asyncio module for handling asynchronous operations
from discord import Intents  # Import the Intents class from discord module
from components.classbuttons import CLView

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

        def __init__(
            self,
            race,
            label,
            view,
            ctx,
            num_dice,
            sides,
            race_name,
            dndclass,
            dndclass_name,
        ):
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
            self.dndclass_name = dndclass_name
            self.dndclass = dndclass
            # Determine button style based on race
            style = (
                discord.ButtonStyle.red  # Set button style to red for specific races
                if race in ["Dragonborn", "Tiefling", "Half-Orc", "Gnome"]
                else (
                    discord.ButtonStyle.green  # Set button style to green for specific races
                    if race in ["Dwarf", "Gnome", "Halfling", "Half-Elf", "Other"]
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
                    class_view = await CLView.create(
                        self.ctx,
                        self._view.character_name,
                        self.dndclass,
                        self.dndclass_name,
                        self.num_dice,
                        self.sides,
                        self.custom_race,
                        modifier=None,
                    )
                    await interaction.followup.send(
                        content="Choose your class:", view=class_view
                    )  # Edit the message to show stats
                except asyncio.TimeoutError:
                    await interaction.followup.send(
                        "Input timed out", ephemeral=True
                    )  # Send message indicating timeout
            else:
                # Prepare stat message and initiate class selection
                class_view = await CLView.create(
                    self.ctx,
                    self._view.character_name,
                    self.dndclass,
                    self.dndclass_name,
                    self.num_dice,
                    self.sides,
                    self.race,
                    modifier=None,
                )
                followup_msg = await interaction.response.edit_message(
                    content="Choose your class:", view=class_view
                )
                try:
                    response = await self.ctx.bot.wait_for(
                        "button_click",
                        check=lambda i: i.user == self.ctx.author,
                        timeout=120,
                    )
                except asyncio.TimeoutError:
                    await class_view.on_timeout()
                    await interaction.edit_original_response(
                        content="Class selection timed out.", view=class_view
                    )

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

    def __init__(
        self,
        ctx,
        character_name,
        num_dice,
        sides,
        race_name,
        dndclass,
        dndclass_name,
        modifier,
    ):
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
        self.dndclass_name = dndclass_name
        self.dndclass = dndclass
        self.modifier = modifier

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
                self.dndclass_name,
                self.dndclass,
            )
            self.add_item(button)  # Add the button to the view

    @classmethod
    async def create(
        cls,
        ctx,
        race,
        num_dice,
        sides,
        race_name,
        dndclass,
        dndclass_name,
        modifier,
    ):
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
        self = RCView(
            ctx,
            race,
            num_dice,
            sides,
            race_name,
            dndclass,
            dndclass_name,
            modifier,
        )  # Initialize the instance
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
