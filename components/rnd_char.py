from character import Character
import discord
from discord.ui import View
import random


class RandView(View):
    """
    A Discord UI view for creating and interacting with a random character.

    Args:
        ctx (discord.Interaction): The context object representing the invocation context.
        character_name (str): The name of the character.
        server_id (int): The ID of the server where the character is being created.
        invoker_id (int): The ID of the user who invoked the command.

    Attributes:
        ctx (discord.Interaction): The context object representing the invocation context.
        character_name (str): The name of the character.
        server_id (int): The ID of the server where the character is being created.
        invoker_id (int): The ID of the user who invoked the command.
        stats (dict): A dictionary containing the character's stats.
        ability_score_modifier (dict): A dictionary containing the character's ability score modifiers.
        character (Character): An instance of the Character class representing the character being created.
        race (str): The race of the character.
        dndclass (str): The class of the character.
        lvl (int): The level of the character.
        hp (int): The hit points of the character.
    """

    def __init__(self, ctx, character_name, server_id, invoker_id, *args, **kwargs):
        """
        Initialize the RandView class.

        Args:
            ctx (discord.Interaction): The context object representing the invocation context.
            character_name (str): The name of the character.
            server_id (int): The ID of the server where the character is being created.
            invoker_id (int): The ID of the user who invoked the command.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.character_name = character_name
        self.server_id = server_id
        self.stats = {
            "Strength": 0,
            "Dexterity": 0,
            "Intelligence": 0,
            "Constitution": 0,
            "Charisma": 0,
            "Wisdom": 0,
        }
        self.ability_score_modifier = {}
        self.character = Character(self.character_name, self.server_id)
        self.invoker_id = invoker_id
        self.race = None
        self.dndclass = None
        self.lvl = None
        self.hp = None

    async def disable_buttons(self):
        """
        Disables all buttons in the view.
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

    async def determine_random_stats(self):
        """
        Determine the character's random stats using 4d6 dice rolls.

        Returns:
            int: The sum of the three highest rolls.
        """
        rolls = [random.randint(1, 6) for _ in range(4)]  # Roll 4d6
        rolls.sort()  # Sort the rolls in ascending order
        return sum(rolls[1:])  # Return the sum of the three highest rolls

    async def random_class_race(self):
        """
        Randomly select the character's class and race.

        Returns:
            tuple: A tuple containing the character's class and race.
        """
        # Choose a random class and race from predefined lists
        dndclass = random.choice(
            [
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
            ]
        )
        race = random.choice(
            [
                "Dragonborn",
                "Dwarf",
                "Elf",
                "Gnome",
                "Half-Elf",
                "Half-Orc",
                "Halfling",
                "Human",
                "Tiefling",
            ]
        )
        return dndclass, race

    async def create_char(self):
        """
        Create the character by rolling stats, determining class and race, and calculating hit points.

        Returns:
            str: A formatted string containing the character's stats.
        """
        await self.character.roll_stats(4, 6)  # Roll stats using 4d6
        self.lvl = 1  # Set the character's level to 1
        self.dndclass, self.race = (
            await self.random_class_race()
        )  # Determine class and race
        self.hp = await self.character.determine_start_hp(
            self.race
        )  # Calculate hit points
        return await self.character.show_stats(
            self.ctx, self.race, self.dndclass, self.lvl, self.hp
        )  # Show the character's stats

    @discord.ui.button(label="No", custom_id="nobutton", style=discord.ButtonStyle.red)
    async def nobutton_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback method for the 'No' button.

        Args:
            interaction (discord.Interaction): The interaction object representing the button click.
            button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user.id == self.invoker_id:  # Check if the user is the invoker
            await self.disable_buttons()  # Disable all buttons
            stats_message = await self.character.show_stats(
                self.ctx, self.race, self.dndclass, self.lvl, self.hp
            )  # Show the character's stats
            await interaction.response.edit_message(
                content=f"{stats_message}\nCharacter has not been saved.", view=self
            )  # Edit the message to indicate that the character has not been saved
        else:
            await interaction.response.send_message(
                content="This is not your decision to make. :point_up: :nerd:",
                ephemeral=True,
                delete_after=15,
            )  # Send a message indicating that it's not the user's decision to make

    @discord.ui.button(
        label="Yes", custom_id="ybutton", style=discord.ButtonStyle.green
    )
    async def yesbutton_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback method for the 'Yes' button.

        Args:
            interaction (discord.Interaction): The interaction object representing the button click.
            button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user.id == self.invoker_id:  # Check if the user is the invoker
            await self.disable_buttons()  # Disable all buttons
            stats_message = await self.character.show_stats(
                self.ctx, self.race, self.dndclass, self.lvl, self.hp
            )  # Show the character's stats
            await self.character.save_to_csv(  # Save the character's stats to a CSV file
                self.character_name,
                self.race,
                self.ctx,
                self.dndclass,
                self.invoker_id,
                self.lvl,
                self.hp,
            )
            await interaction.response.edit_message(
                content=f"{stats_message}\nCharacter has been saved.", view=self
            )  # Edit the message to indicate that the character has been saved
        else:
            await interaction.response.send_message(
                content="This is not your decision to make. :point_up: :nerd:",
                ephemeral=True,
                delete_after=15,
            )  # Send a message indicating that it's not the user's decision to make
