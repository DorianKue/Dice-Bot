import discord
from character import Character
from yn_buttons import YView


class CLView(discord.ui.View):
    """
    A view for selecting character class using buttons.
    """

    class ClassButton(discord.ui.Button):
        """
        Represents a button for selecting a character class.
        """

        def __init__(
            self,
            dndclass,
            label,
            view,
            ctx,
            dndclass_name,
            num_dice,
            sides,
            race_name,
            invoker_id,
        ):
            """
            Initializes the ClassButton instance.

            Args:
                dndclass (str): The D&D character class.
                label (str): The label to display on the button.
                view (CLView): The parent view object.
                ctx: The context object representing the invocation context.
                dndclass_name (str): The name of the character's class.
                num_dice (int): The number of dice.
                sides (int): The number of sides on the dice.
                race_name (str): The name of the character's race.
                invoker_id (int): The ID of the user who invoked the command.
            """
            # Initialize button properties
            self.num_dice = num_dice
            self.sides = sides
            self.ctx = ctx
            self._view = view
            self.dndclass = dndclass
            self.dndnclass_name = dndclass_name
            self.race_name = race_name
            self.invoker_id = invoker_id
            # Determine button style based on character class
            style = (
                discord.ButtonStyle.red
                if dndclass in ["Barbarian", "Fighter", "Paladin", "Cleric"]
                else (
                    discord.ButtonStyle.green
                    if dndclass in ["Monk", "Ranger", "Rogue", "Druid"]
                    else discord.ButtonStyle.blurple
                )
            )
            row = (
                0
                if dndclass in ["Barbarian", "Fighter", "Paladin", "Cleric"]
                else 1 if dndclass in ["Monk", "Ranger", "Rogue", "Druid"] else 2
            )
            # Initialize button using superclass constructor
            super().__init__(label=label, style=style, custom_id=dndclass, row=row)

        async def callback(self, interaction: discord.Interaction):
            """
            Callback function for the button.

            Args:
                interaction (discord.Interaction): The interaction object.
            """
            # Check if button interaction is valid
            if self.view and not await self.view.button_check(interaction):
                return
            # Disable all buttons
            await self.view.disable_buttons()
            # Create a Character instance
            player = Character(self._view.character_name, self._view.ctx.guild.id)
            # Roll character stats
            player.roll_stats(self.num_dice, self.sides)
            # Get stats table
            stats_table = player.show_stats(self.ctx, self.race_name, self.dndclass)
            # Create YView for reroll prompt
            reroll_view = YView(
                interaction,
                self.num_dice,
                self.sides,
                self._view.character_name,
                player,
                self.race_name,
                self.dndclass,
                self.invoker_id,
            )
            # Construct message content
            stat_msg_content = f"{stats_table}Would you like to reroll?"
            # Edit the interaction response with new content and view
            await interaction.response.edit_message(
                content=stat_msg_content, view=reroll_view
            )

        @property
        def view(self):
            return self._view

        @view.setter
        def view(self, dndclass):
            self._view = dndclass

    async def disable_buttons(self):
        """
        Disable all buttons in the view.
        """
        # Iterate through all children of the view
        for child in self.children:
            # Check if the child is a Button
            if isinstance(child, discord.ui.Button):
                # Disable the button
                child.disabled = True
                # Set the button style to gray
                child.style = discord.ButtonStyle.gray

    def __init__(
        self,
        ctx,
        character_name,
        dndclass,
        dndclass_name,
        num_dice,
        sides,
        race_name,
        invoker_id,
    ):
        """
        Initializes the CLView instance.

        Args:
            ctx: The context object representing the invocation context.
            character_name (str): The name of the character.
            dndclass (str): The D&D character class.
            dndclass_name (str): The name of the character's class.
            num_dice (int): The number of dice.
            sides (int): The number of sides on the dice.
            race_name (str): The name of the character's race.
            invoker_id (int): The ID of the user who invoked the command.
        """
        # Initialize the parent class
        super().__init__()
        # Set instance variables
        self.ctx = ctx
        self.character_name = character_name
        self.dndclass = dndclass
        self.dndclass_name = dndclass_name
        self.command_invoker_id = ctx.author.id
        self.num_dice = num_dice
        self.sides = sides
        self.race_name = race_name
        self.invoker_id = invoker_id

    async def add_buttons(self, dndclass_name):
        """
        Add buttons for selecting character class.

        Args:
            dndclass_name (str): The name of the character's class.
        """
        # Iterate through D&D character classes
        for dndclass in [
            "Barbarian",
            "Fighter",
            "Paladin",
            "Monk",
            "Ranger",
            "Rogue",
            "Bard",
            "Cleric",
            "Druid",
            "Sorcerer",
            "Warlock",
            "Wizard",
            "Artificer",
        ]:
            # Create a button for each class
            button = self.ClassButton(
                dndclass,
                dndclass,
                self.ctx,
                self.character_name,
                dndclass_name,
                self.num_dice,
                self.sides,
                self.race_name,
                self.invoker_id,
            )
            # Add the button to the view
            self.add_item(button)

    @classmethod
    async def create(
        cls, ctx, character_name, dndclass, dndclass_name, num_dice, sides, race_name
    ):
        """
        Create an instance of CLView.

        Args:
            ctx: The context object representing the invocation context.
            character_name (str): The name of the character.
            dndclass (str): The D&D character class.
            dndclass_name (str): The name of the character's class.
            num_dice (int): The number of dice.
            sides (int): The number of sides on the dice.
            race_name (str): The name of the character's race.

        Returns:
            CLView: An instance of CLView.
        """
        # Get the ID of the user who invoked the command
        invoker_id = ctx.author.id
        # Create an instance of CLView
        self = CLView(
            ctx,
            character_name,
            dndclass,
            dndclass_name,
            num_dice,
            sides,
            race_name,
            invoker_id,
        )
        # Add buttons for selecting character class
        await self.add_buttons(dndclass_name)
        return self

    async def on_timeout(self):
        """
        Handler for when the view times out.
        """
        # Disable all buttons in the view
        await self.disable_buttons()

    async def button_check(self, interaction: discord.Interaction):
        """
        Check if the button interaction is valid.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            bool: True if the button interaction is valid, False otherwise.
        """
        # Check if the user who interacted with the button is the command invoker
        if interaction.user.id != self.command_invoker_id:
            # Send error message for invalid user
            await interaction.response.send_message(
                content="This is not your decision to make. :point_up: :nerd:",
                ephemeral=True,  # Make the error message ephemeral
                delete_after=10,  # Set the deletion time for the error message
            )
            return False  # Return False for invalid interaction
        return True  # Return True for valid interaction
