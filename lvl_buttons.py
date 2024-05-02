from character import (
    Character,
)  # Importing the Character class from the character module
import discord  # Importing the discord module


class MyView(discord.ui.View):  # Defining a custom Discord UI view
    class StatButton(
        discord.ui.Button
    ):  # Defining a custom button class for managing character stats
        """
        Represents a button for updating character stats.

        Attributes:
            stat_name (str): The name of the stat associated with the button.
            max_clicks (int): The maximum number of clicks allowed for the button.
            view (MyView): The MyView instance to which the button belongs.
        """

        def __init__(
            self, stat_name, label, max_clicks, view
        ):  # Initializing the StatButton object
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
                # Determine button style based on stat_name
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
                # Determine button row based on stat_name
                row=0 if stat_name in ["Strength", "Dexterity", "Intelligence"] else 1,
            )
            self.stat_name = stat_name
            self.max_clicks = max_clicks
            self._view = view

        @property
        def view(self):  # Getter method for accessing the MyView instance
            """MyView: The MyView instance to which the button belongs."""
            return self._view

        @view.setter
        def view(self, value):  # Setter method for setting the MyView instance
            """Sets the MyView instance to which the button belongs."""
            self._view = value

        async def callback(
            self, interaction: discord.Interaction
        ):  # Callback method for handling button interactions
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
                await self.view.update_character_stat(self.stat_name)
                await interaction.response.edit_message(
                    content=f"{self.stat_name} increased by 1", view=self.view
                )
                await self.view.check_completion()
            else:
                await self.view.disable_buttons()

    def __init__(
        self, ctx, char_name, stats_table_message, max_clicks=2
    ):  # Initializing the MyView object
        """
        Initializes the MyView object.

        Args:
            ctx (discord.ext.commands.Context): The context in which the view is created.
            char_name (str): The name of the character whose stats are being managed.
            stats_table_message (discord.Message): The message displaying the character's stats table.
            max_clicks (int, optional): The maximum number of times a user can click the buttons to increase stats. Defaults to 2.
        """
        super().__init__()  # Calling the constructor of the parent class
        self.ctx = ctx  # Storing the context in which the view is created
        self.char_name = char_name  # Storing the name of the character
        self.max_clicks = max_clicks  # Storing the maximum number of clicks allowed
        self.click_count = 0  # Initializing the click count to zero
        self.message = None  # Initializing the message attribute
        self.stats_table_message = stats_table_message  # Storing the message displaying the character's stats table
        self.command_invoker_id = (
            ctx.author.id
        )  # Storing the ID of the user who invoked the command

        self.add_buttons()  # Adding buttons to the view

    def add_buttons(self):  # Method to add stat buttons to the view
        """Adds stat buttons to the view."""
        for stat_name in [
            "Strength",
            "Dexterity",
            "Intelligence",
            "Constitution",
            "Charisma",
            "Wisdom",
        ]:
            button = self.StatButton(stat_name, stat_name, self.max_clicks, self)
            self.add_item(button)

    async def update_character_stat(
        self, selected_stat
    ):  # Method to update character stats
        """
        Updates the character's stat.

        Args:
            selected_stat (str): The name of the stat to update.
        """
        await Character.update_character_stat(self.ctx, self.char_name, selected_stat)
        updated_stats_message = await Character.display_character_stats_lvl(
            self.ctx, self.char_name, self.ctx.guild.id, self.stats_table_message
        )
        self.stats_table_message = (
            updated_stats_message  # Updating the stats_table_message attribute
        )
        self.click_count += 1  # Incrementing the click count

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
    ):  # Method to check if the max click count is reached
        """Checks if the max click count is reached and handles accordingly."""
        if (
            self.click_count >= self.max_clicks
        ):  # Checking if the click count exceeds the maximum allowed clicks
            await self.disable_buttons()  # Disabling all buttons in the view
            await self.message.edit(  # Editing the message to indicate completion
                content="Out of attribute points to spend.", view=self
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
                "You don't have permission to do that.", ephemeral=True
            )  # Sending an ephemeral message
            return False  # Returning False if user is not the command invoker
        return True  # Returning True if user is the command invoker
