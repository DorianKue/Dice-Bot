import os
import csv
import discord


class RView(discord.ui.View):
    """
    A custom Discord UI view for confirming deletion of a character.

    Attributes:
        ctx (discord.Context): The context of the command.
        name (str): The name of the character to be deleted.
    """

    def __init__(self, ctx, name: str):
        """
        Initializes the RView object.

        Args:
            ctx (discord.Context): The context of the command.
            name (str): The name of the character to be deleted.
        """
        self.ctx = ctx  # Store the context of the command
        self.name = name
        super().__init__()  # Call the __init__() method of the parent class

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
        Disables all buttons in the view on timeout.
        """
        await self.disable_buttons()  # Disable all buttons in the view

    @discord.ui.button(label="No", custom_id="nbutton", style=discord.ButtonStyle.green)
    async def nobutton_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback function for the 'No' button.

        Args:
            interaction (discord.Interaction): The interaction that triggered the button.
            button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user == self.ctx.author:
            await self.disable_buttons()
            await interaction.response.edit_message(
                content="Deletion canceled :smiling_face_with_tear:",
                view=self,
                delete_after=60,
            )
        else:
            await interaction.response.send_message(
                "This is not your decision to make. :point_up: :nerd:",
                ephemeral=True,
                delete_after=10,
            )

    @discord.ui.button(label="Yes", custom_id="ybutton", style=discord.ButtonStyle.red)
    async def yesbutton_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback function for the 'Yes' button.

        Args:
            interaction (discord.Interaction): The interaction that triggered the button.
            button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user == self.ctx.author:
            # Construct server directory name based on guild ID
            server_dir = f"server_{self.ctx.guild.id}"
            # Construct filename
            filename = f"{self.name}_stats.csv"
            # Construct full filepath
            filepath = os.path.join(server_dir, filename)

            # Open the character's stats file
            with open(filepath, newline="") as file:
                # Create a CSV DictReader object
                reader = csv.DictReader(file)
                # Iterate through each row in the CSV
                for row in reader:
                    creator_id = None
                    # Check if the row corresponds to the character name
                    if row["Name"].lower() == self.name.lower():
                        if creator_id is None:
                            creator_id = row["CreatorID"]
                            break

            await self.disable_buttons()

            # If creator ID not found
            if creator_id is None:
                # If the invoker is an administrator, delete the file
                if self.ctx.author.guild_permissions.administrator:
                    os.remove(filepath)
                    # Confirm deletion
                    await interaction.response.edit_message(
                        content=f"Character '{self.name}' deleted successfully. :headstone:",
                        view=self,
                    )
                else:
                    # Notify that an admin can remove the file
                    await interaction.response.send_message(
                        content=f"Unable to determine creator of character '{self.name}'. An admin will be able to remove the file.",
                        ephemeral=True,
                    )
            # If the invoker is the creator or an administrator, delete the file
            elif (
                self.ctx.author.id == creator_id
                or self.ctx.author.guild_permissions.administrator
            ):
                os.remove(filepath)
                # Confirm deletion
                await interaction.response.edit_message(
                    content=f"Character '{self.name}' deleted successfully. :headstone:",
                    view=self,
                )
        else:
            # Send error message if unauthorized to delete
            await interaction.response.send_message(
                "You can't delete the character of someone else. :rage:",
                ephemeral=True,
                delete_after=10,
            )
