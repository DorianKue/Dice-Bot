import os  # Import the os module for operating system functionalities
import csv  # Import the csv module for reading and writing CSV files
import discord  # Import the discord module for Discord API functionalities


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
            server_dir = (
                f"server_{self.ctx.guild.id}"  # Construct server directory name
            )
            filename = f"{self.name}_stats.csv"  # Construct filename
            filepath = os.path.join(server_dir, filename)  # Construct full filepath

            with open(filepath, newline="") as file:  # Open the character's stats file
                reader = csv.DictReader(file)  # Create a CSV DictReader object
                creator_id = None
                for row in reader:  # Iterate through each row in the CSV
                    if (
                        row["Name"].lower() == self.name
                    ):  # Check if the row corresponds to the character name
                        creator_id = int(
                            row.get("CreatorID", 0)
                        )  # Get the ID of the creator from the CSV
                        break  # Stop iterating if the character is found
                if creator_id is None:  # If creator ID not found
                    if not os.access(server_dir, os.R_OK):  # Check directory access
                        await self.ctx.send(
                            f"Unable to access '{self.name}' savefile.",
                            ephemeral=True,
                            delete_after=30,
                        )  # Send error message if access is denied
                        return

                    await self.ctx.send(
                        f"Unable to determine creator of character '{self.name}'.",
                        ephemeral=True,
                    )  # Send error message if creator ID not found
                    return
            await self.disable_buttons()  # Disable all buttons
            if (
                self.ctx.author.id == creator_id
                or self.ctx.author.guild_permissions.administrator
            ):  # Check if user is authorized to delete
                os.remove(filepath)  # Delete the file
                await interaction.response.edit_message(
                    content=f"{self.name} deleted successfully. :headstone:", view=self
                )  # Confirm deletion
        else:
            await interaction.response.send_message(
                "You can't delete the character of someone else. :rage:",
                ephemeral=True,
                delete_after=10,
            )  # Send error message if unauthorized
