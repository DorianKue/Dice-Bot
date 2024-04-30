from character import Character  # Importing the Character class from bot_class module
import discord  # Importing the discord module


class MyView(discord.ui.View):  # Defining a custom Discord UI view
    """
    A custom Discord UI view for managing character stats.

    Attributes:
        ctx (discord.ext.commands.Context): The context in which the view is created.
        char_name (str): The name of the character whose stats are being managed.
        stats_table_message (discord.Message): The message displaying the character's stats table.
        max_clicks (int): The maximum number of times a user can click the buttons to increase stats.
        click_count (int): The current count of button clicks.
        message (discord.Message): The message to which the view is attached.
        command_invoker_id (int): The ID of the user who invoked the command to create the view.
    """

    def __init__(
        self, ctx, char_name, stats_table_message, max_clicks=2
    ):  # Initializing the MyView object
        """Initialize the MyView object."""
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

    async def update_character_stat(
        self, selected_stat
    ):  # Method to update the character's stat
        """Update the character's stat."""
        await Character.update_character_stat(
            self.ctx, self.char_name, selected_stat
        )  # Updating the character's stat
        updated_stats_message = await Character.display_character_stats_lvl(  # Displaying the updated stats message
            self.ctx, self.char_name, self.ctx.guild.id, self.stats_table_message
        )
        self.stats_table_message = (
            updated_stats_message  # Updating the stats_table_message attribute
        )
        self.click_count += 1  # Incrementing the click count

    async def disable_buttons(self):  # Method to disable all buttons in the view
        """Disable all buttons in the view."""
        for child in self.children:  # Iterating through each child element in the view
            if isinstance(
                child, discord.ui.Button
            ):  # Checking if the child element is a Button
                child.disabled = True  # Disabling the button
                child.style = discord.ButtonStyle.gray  # Setting button style to gray

    async def check_completion(
        self,
    ):  # Method to check if the max click count is reached
        """Check if the max click count is reached."""
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
        """Disable buttons when the view times out."""
        await self.disable_buttons()  # Disabling all buttons in the view
        await self.message.edit(
            view=self
        )  # Editing the message to reflect disabled buttons

    async def button_check(
        self, interaction
    ):  # Method to check if the interaction user is the command invoker
        """
        Check if the interaction user is the command invoker.

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

    @discord.ui.button(
        label="Strength", row=0, style=discord.ButtonStyle.red
    )  # Defining a button for Strength
    async def str_button_callback(
        self, interaction, button
    ):  # Callback function for the Strength button
        """Callback function for the Strength button."""
        if not await self.button_check(
            interaction
        ):  # Checking if the interaction user is not the command invoker
            return  # Returning if user is not the command invoker
        if (
            self.click_count < self.max_clicks
        ):  # Checking if the click count is within the maximum allowed clicks
            await self.update_character_stat(
                "Strength"
            )  # Updating the character's Strength stat
            await interaction.response.edit_message(  # Editing the message to reflect stat increase
                content="Strength increased by 1", view=self
            )
            await self.check_completion()  # Checking if max click count is reached
        else:  # Executed when max click count is reached
            await self.disable_buttons()  # Disabling all buttons in the view

    @discord.ui.button(  # Defining a button for Dexterity
        label="Dexterity", row=0, custom_id="dex", style=discord.ButtonStyle.green
    )
    async def dex_button_callback(
        self, interaction, button
    ):  # Callback function for the Dexterity button
        """Callback function for the Dexterity button."""
        if not await self.button_check(
            interaction
        ):  # Checking if the interaction user is not the command invoker
            return  # Returning if user is not the command invoker
        if (
            self.click_count < self.max_clicks
        ):  # Checking if the click count is within the maximum allowed clicks
            await self.update_character_stat(
                "Dexterity"
            )  # Updating the character's Dexterity stat
            await interaction.response.edit_message(  # Editing the message to reflect stat increase
                content="Dexterity increased by 1", view=self
            )
            await self.check_completion()  # Checking if max click count is reached
        else:  # Executed when max click count is reached
            await self.disable_buttons()  # Disabling all buttons in the view

    @discord.ui.button(  # Defining a button for Intelligence
        label="Intelligence", row=0, custom_id="int", style=discord.ButtonStyle.blurple
    )
    async def int_button_callback(
        self, interaction, button
    ):  # Callback function for the Intelligence button
        """Callback function for the Intelligence button."""
        if not await self.button_check(
            interaction
        ):  # Checking if the interaction user is not the command invoker
            return  # Returning if user is not the command invoker
        if (
            self.click_count < self.max_clicks
        ):  # Checking if the click count is within the maximum allowed clicks
            await self.update_character_stat(
                "Intelligence"
            )  # Updating the character's Intelligence stat
            await interaction.response.edit_message(  # Editing the message to reflect stat increase
                content="Intelligence increased by 1", view=self
            )
            await self.check_completion()  # Checking if max click count is reached
        else:  # Executed when max click count is reached
            await self.disable_buttons()  # Disabling all buttons in the view

    @discord.ui.button(
        label="Constitution", row=1, custom_id="const", style=discord.ButtonStyle.red
    )
    async def const_button_callback(self, interaction, button):
        """Callback function for the Constitution button."""
        # Check if the interaction user is the command invoker
        if not await self.button_check(interaction):
            return
        # Check if the maximum click count is reached
        if self.click_count < self.max_clicks:
            # Update the character's Constitution stat
            await self.update_character_stat("Constitution")
            # Edit the response message to indicate the increase in Constitution
            await interaction.response.edit_message(
                content="Constitution increased by 1", view=self
            )
            # Check if the max click count is reached after the update
            await self.check_completion()
        else:
            # Disable buttons if the max click count is reached
            await self.disable_buttons()

    @discord.ui.button(
        label="Charisma", row=1, custom_id="cha", style=discord.ButtonStyle.green
    )
    async def cha_button_callback(self, interaction, button):
        """Callback function for the Charisma button."""
        # Check if the interaction user is the command invoker
        if not await self.button_check(interaction):
            return
        # Check if the maximum click count is reached
        if self.click_count < self.max_clicks:
            # Update the character's Charisma stat
            await self.update_character_stat("Charisma")
            # Edit the response message to indicate the increase in Charisma
            await interaction.response.edit_message(
                content="Charisma increased by 1", view=self
            )
            # Check if the max click count is reached after the update
            await self.check_completion()
        else:
            # Disable buttons if the max click count is reached
            await self.disable_buttons()

    @discord.ui.button(
        label="Wisdom", row=1, custom_id="wis", style=discord.ButtonStyle.blurple
    )
    async def wis_button_callback(self, interaction, button):
        """Callback function for the Wisdom button."""
        # Check if the interaction user is the command invoker
        if not await self.button_check(interaction):
            return
        # Check if the maximum click count is reached
        if self.click_count < self.max_clicks:
            # Update the character's Wisdom stat
            await self.update_character_stat("Wisdom")
            # Edit the response message to indicate the increase in Wisdom
            await interaction.response.edit_message(
                content="Wisdom increased by 1", view=self
            )
            # Check if the max click count is reached after the update
            await self.check_completion()
        else:
            # Disable buttons if the max click count is reached
            await self.disable_buttons()
