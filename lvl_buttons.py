from character import (
    Character,
)  # Importing the Character class from the character module
import discord  # Importing the discord module
import os
import csv
from tabulate import tabulate


class MyView(discord.ui.View):
    class StatButton(discord.ui.Button):
        """
        Represents a button for updating character stats.

        Attributes:
            stat_name (str): The name of the stat associated with the button.
            max_clicks (int): The maximum number of clicks allowed for the button.
            view (MyView): The MyView instance to which the button belongs.
        """

        def __init__(self, stat_name, label, max_clicks, view, stats_content):
            """
            Initializes the StatButton object.

            Args:
                stat_name (str): The name of the stat associated with the button.
                label (str): The label text displayed on the button.
                max_clicks (int): The maximum number of clicks allowed for the button.
                view (MyView): The MyView instance to which the button belongs.
            """
            super().__init__(
                label=label,
                style=(
                    discord.ButtonStyle.red
                    if stat_name in ["Strength", "Constitution"]
                    else (
                        discord.ButtonStyle.green
                        if stat_name in ["Dexterity", "Charisma"]
                        else discord.ButtonStyle.blurple
                    )
                ),
                custom_id=stat_name,
                row=0 if stat_name in ["Strength", "Dexterity", "Intelligence"] else 1,
            )
            self.stat_name = stat_name  # Assigning the stat name to the button
            self.max_clicks = max_clicks  # Assigning the maximum clicks allowed
            self._view = (
                view  # Assigning the MyView instance to which the button belongs
            )
            self.stats_content = stats_content

        @property
        def view(self):
            """MyView: The MyView instance to which the button belongs."""
            return self._view

        @view.setter
        def view(self, value):
            """Sets the MyView instance to which the button belongs."""
            self._view = value

        async def callback(self, interaction: discord.Interaction):
            """
            Handles button callback interaction.

            Args:
                interaction (discord.Interaction): The interaction object representing the button click.
            """
            # Check if the user is allowed to interact with the button
            if self.view and not await self.view.button_check(interaction):
                return

            # Update character stat if click count is within limits
            if self.view and self.view.click_count < self.max_clicks:
                # Update the character stat
                await self.view.update_character_stat(self.stat_name)

                # Get the updated stats message content
                increase_message = f"{self.stat_name} increased by 1"
                self.view.stats_content = await self.view.send_message(
                    increase_message=increase_message
                )

                # Edit the message to include both the updated stats and the "increased by 1" message
                await interaction.response.edit_message(
                    content=f"{self.view.stats_content}{increase_message}",
                    view=self.view,
                )

                await self.view.check_completion()  # Check if the max click count is reached
            else:
                await self.view.disable_buttons()  # Disable all buttons

    def __init__(self, ctx, char_name, stats_table_message, max_clicks=2):
        """
        Initializes the MyView object.

        Args:
            ctx (discord.ext.commands.Context): The context in which the view is invoked.
            char_name (str): The name of the character.
            stats_table_message (discord.Message): The message containing the character's stats table.
            max_clicks (int, optional): The maximum number of clicks allowed for each button. Defaults to 2.
        """
        super().__init__()
        self.ctx = ctx  # Store the context
        self.char_name = char_name  # Store the character name
        self.max_clicks = max_clicks  # Store the maximum clicks allowed
        self.click_count = 0  # Initialize click count to 0
        self.message = None  # Initialize message to None
        self.stats_table_message = stats_table_message  # Store the stats table message
        self.command_invoker_id = ctx.author.id  # Store the command invoker ID

    @classmethod
    async def create(cls, ctx, char_name, stats_table_message, max_clicks=2):
        """
        Creates a new instance of MyView.

        Args:
            cls: The class reference.
            ctx (discord.ext.commands.Context): The context in which the view is invoked.
            char_name (str): The name of the character.
            stats_table_message (discord.Message): The message containing the character's stats table.
            max_clicks (int, optional): The maximum number of clicks allowed for each button. Defaults to 2.

        Returns:
            MyView: The created MyView instance.
        """
        # Create a new instance of MyView with the provided parameters
        self = MyView(ctx, char_name, stats_table_message, max_clicks)
        # Add buttons to the view instance
        await self.add_buttons()
        return self

    async def add_buttons(self):
        """
        Adds buttons for each character stat.
        """
        # Send a message containing the character's stats table and store its content
        self.stats_content = await self.send_message()
        # Iterate over each character stat and create a button for it
        for stat_name in [
            "Strength",
            "Dexterity",
            "Intelligence",
            "Constitution",
            "Charisma",
            "Wisdom",
        ]:
            # Create a new button instance for the current stat
            button = self.StatButton(
                stat_name,
                stat_name,
                self.max_clicks,
                self,
                self.stats_content,
            )  # Create a new button
            # Add the button to the view
            self.add_item(button)

    async def update_character_stat(self, selected_stat):
        """
        Updates the character's stat and sends a message.

        Args:
            selected_stat (str): The name of the selected stat to update.
        """
        await Character.update_character_stat(
            self.ctx, self.char_name, selected_stat
        )  # Update character stat
        self.click_count += 1  # Increment click count

    async def disable_buttons(self):  # Method to disable all buttons in the view
        """Disables all buttons in the view."""
        for child in self.children:  # Iterating through each child element in the view
            if isinstance(
                child, discord.ui.Button
            ):  # Checking if the child element is a Button
                child.disabled = True  # Disabling the button
                child.style = discord.ButtonStyle.gray  # Setting button style to gray

    async def check_completion(
        self,
    ):
        """Method to check if the max click count is reached."""
        if self.click_count >= self.max_clicks:
            # Checking if the click count exceeds the maximum allowed clicks
            await self.disable_buttons()
            if self.message:
                # Edit the message to indicate completion without removing the stats table
                await self.message.edit(
                    content=f"{self.stats_content}Out of attribute points to spend.",
                    view=self,
                )

    async def on_timeout(
        self,
    ):  # Method to handle button disablement when the view times out
        """Handles button disablement when the view times out."""
        await self.disable_buttons()  # Disabling all buttons in the view
        await self.message.edit(
            view=self
        )  # Editing the message to reflect disabled buttons

    async def button_check(
        self, interaction
    ):  # Method to check if the interaction user is the command invoker
        """
        Checks if the interaction user is the command invoker.

        Args:
            interaction (discord.Interaction): The interaction to check.

        Returns:
            bool: True if the user is the command invoker, False otherwise.
        """
        if (
            interaction.user.id != self.command_invoker_id
        ):  # Checking if the interaction user is not the command invoker
            await interaction.response.send_message(
                "This is not your decision to make. :point_up: :nerd:", ephemeral=True
            )  # Sending an ephemeral message
            return False  # Returning False if user is not the command invoker
        return True  # Returning True if user is the command invoker

    async def send_message(self, increase_message=None):
        """Send a message containing the character's stats table and the stat buttons."""
        # Display character stats in a tabulated format
        self.stats_content = await self.display_character_stats_lvl(
            self.ctx, self.char_name, self.ctx.guild.id, self.stats_table_message
        )

        # Create a string containing the button instructions
        message_content = f"{self.stats_content}"
        if increase_message:
            message_content += f"{increase_message}"
        else:
            message_content += "Select which attribute you want to increase:"

        # Check if a message already exists
        if self.message:
            # Update the existing message with the new content and view
            await self.message.edit(content=message_content, view=self)
        else:
            # Send a new message with the content and view
            message = await self.ctx.send(content=message_content, view=self)
            self.message = message

        return self.stats_content  # Return the stats table content for later use

    @staticmethod
    async def display_character_stats_lvl(
        ctx, char_name, server_id, stats_message=None
    ):
        try:
            # Construct directory path based on server ID
            server_dir = f"server_{server_id}"
            # Construct the full file path
            filepath = os.path.join(server_dir, f"{char_name}_stats.csv")
            # Open the CSV file
            with open(filepath, newline="") as file:
                # Create a CSV DictReader
                reader = csv.DictReader(file)
                # Initialize a list to store stats
                stats = []
                # Iterate through each row in the CSV
                for row in reader:
                    # Get the modifier and convert to int
                    modifier = int(row["Modifier"])
                    # Check if modifier is greater than or equal to 1
                    if modifier >= 1:
                        modifier_str = f"+{modifier}"
                    else:
                        modifier_str = str(modifier)
                    # Append attribute, value, and modified modifier to stats list
                    stats.append([row["Attribute"], row["Value"], modifier_str])
                # Define headers for the tabulated output
                headers = ["Attribute", "Value", "Modifier"]
                # Generate a tabulated representation of the stats
                stats_table = tabulate(stats, headers=headers, tablefmt="grid")

            # Return the stats table content
            return f"```{stats_table}```"

        except Exception as e:
            # Raise an exception if an error occurs
            raise RuntimeError(f"An error occurred: {e}")
