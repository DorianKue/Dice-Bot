from character import (
    Character,
)  # Importing the Character class from the character module
import discord  # Importing the discord library


class MyView(discord.ui.View):
    """
    Custom view for managing character attribute points in a Discord bot.

    Args:
        ctx (discord.ext.commands.Context): The context of the command.
        char_name (str): The name of the character to update.
        max_clicks (int, optional): Maximum number of attribute points to spend. Defaults to 2.
    """

    def __init__(self, ctx, char_name, max_clicks=2):
        super().__init__()  # Calling the constructor of the parent class (discord.ui.View)
        self.ctx = ctx  # Storing the context of the command
        self.char_name = char_name  # Storing the name of the character
        self.max_clicks = (
            max_clicks  # Storing the maximum number of attribute points to spend
        )
        self.click_count = 0  # Initializing the count of attribute point clicks to 0

    async def update_character_stat(self, selected_stat):
        """
        Update the character's attribute based on the selected stat.

        Args:
            selected_stat (str): The attribute to update.
        """
        await Character.update_character_stat(
            self.ctx, self.char_name, selected_stat
        )  # Calling a method to update the character's attribute
        self.click_count += 1  # Incrementing the count of attribute point clicks

    async def disable_buttons(self):
        """Disable all buttons in the view."""
        for child in self.children:  # Iterating through all the children of the view
            if isinstance(
                child, discord.ui.Button
            ):  # Checking if the child is a Button
                child.disabled = True  # Disabling the button
                child.style = (
                    discord.ButtonStyle.gray
                )  # Setting the button style to gray

    async def check_completion(self):
        """Check if the maximum number of attribute points has been reached and disable buttons if so."""
        if (
            self.click_count >= self.max_clicks
        ):  # Checking if the maximum clicks have been reached
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached
            await self.message.edit(  # Editing the message to display a notification
                content="Out of attribute points to spend.", view=self
            )

    async def on_timeout(self):
        """Handler for when the view times out."""
        await self.disable_buttons()  # Disabling all buttons when the view times out
        await self.message.edit(
            view=self
        )  # Editing the message to reflect the disabled buttons

    # Button callbacks for increasing various attributes

    @discord.ui.button(label="Strength", row=0, style=discord.ButtonStyle.red)
    async def str_button_callback(self, interaction, button):
        """Callback for the Strength button."""
        if (
            self.click_count < self.max_clicks
        ):  # Checking if maximum clicks have not been reached
            await self.update_character_stat(
                "Strength"
            )  # Updating character's Strength attribute
            await interaction.response.edit_message(  # Editing the message to notify about the update
                content="Strength increased by 1", view=self
            )
            await self.check_completion()  # Checking if maximum clicks have been reached
        else:
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached

    @discord.ui.button(
        label="Dexterity", row=0, custom_id="dex", style=discord.ButtonStyle.green
    )
    async def dex_button_callback(self, interaction, button):
        """Callback for the Dexterity button."""
        if (
            self.click_count < self.max_clicks
        ):  # Checking if maximum clicks have not been reached
            await self.update_character_stat(
                "Dexterity"
            )  # Updating character's Dexterity attribute
            await interaction.response.edit_message(  # Editing the message to notify about the update
                content="Dexterity increased by 1", view=self
            )
            await self.check_completion()  # Checking if maximum clicks have been reached
        else:
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached

    @discord.ui.button(
        label="Intelligence", row=0, custom_id="int", style=discord.ButtonStyle.blurple
    )
    async def int_button_callback(self, interaction, button):
        """Callback for the Intelligence button."""
        if (
            self.click_count < self.max_clicks
        ):  # Checking if maximum clicks have not been reached
            await self.update_character_stat(
                "Intelligence"
            )  # Updating character's Intelligence attribute
            await interaction.response.edit_message(  # Editing the message to notify about the update
                content="Intelligence increased by 1", view=self
            )
            await self.check_completion()  # Checking if maximum clicks have been reached
        else:
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached

    @discord.ui.button(
        label="Constitution", row=1, custom_id="const", style=discord.ButtonStyle.red
    )
    async def const_button_callback(self, interaction, button):
        """Callback for the Constitution button."""
        if (
            self.click_count < self.max_clicks
        ):  # Checking if maximum clicks have not been reached
            await self.update_character_stat(
                "Constitution"
            )  # Updating character's Constitution attribute
            await interaction.response.edit_message(  # Editing the message to notify about the update
                content="Constitution increased by 1", view=self
            )
            await self.check_completion()  # Checking if maximum clicks have been reached
        else:
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached

    @discord.ui.button(
        label="Charisma", row=1, custom_id="cha", style=discord.ButtonStyle.green
    )
    async def cha_button_callback(self, interaction, button):
        """Callback for the Charisma button."""
        if (
            self.click_count < self.max_clicks
        ):  # Checking if maximum clicks have not been reached
            await self.update_character_stat(
                "Charisma"
            )  # Updating character's Charisma attribute
            await interaction.response.edit_message(  # Editing the message to notify about the update
                content="Charisma increased by 1", view=self
            )
            await self.check_completion()  # Checking if maximum clicks have been reached
        else:
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached

    @discord.ui.button(
        label="Wisdom", row=1, custom_id="wis", style=discord.ButtonStyle.blurple
    )
    async def wis_button_callback(self, interaction, button):
        """Callback for the Wisdom button."""
        if (
            self.click_count < self.max_clicks
        ):  # Checking if maximum clicks have not been reached
            await self.update_character_stat(
                "Wisdom"
            )  # Updating character's Wisdom attribute
            await interaction.response.edit_message(  # Editing the message to notify about the update
                content="Wisdom increased by 1", view=self
            )
            await self.check_completion()  # Checking if maximum clicks have been reached
        else:
            await self.disable_buttons()  # Disabling all buttons if maximum clicks reached
