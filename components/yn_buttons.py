from character import Character  # Import the Character class from the character module
import discord  # Import the discord module


class YView(
    discord.ui.View
):  # Define a custom view class YView inheriting from discord.ui.View
    """
    A custom view for handling Yes/No buttons.
    """

    def __init__(
        self,
        ctx,
        num_dice,
        sides,
        character_name,
        player,
        race_name,
        dndclass,
        invoker_id,
        modifier,
    ):
        """
        Initializes the YView.

        Args:
            ctx (discord.Context): The context of the command.
            num_dice (int): Number of dice.
            sides (int): Number of sides on each die.
            character_name (str): Name of the character.
        """
        self.ctx = ctx  # Store the context of the command
        self.num_dice = num_dice  # Store the number of dice
        self.sides = sides  # Store the number of sides on each die
        self.character_name = character_name  # Store the name of the character
        self.player = player
        self.race_name = race_name
        self.dndclass = dndclass
        self.invoker_id = invoker_id
        self.modifier = modifier
        super().__init__()  # Call the __init__() method of the parent class

    async def disable_buttons(self):
        """
        Disables all buttons in the view.
        """
        for child in self.children:  # Iterate through all children of the view
            if isinstance(child, discord.ui.Button):  # Check if the child is a Button
                child.disabled = True  # Disable the button
                child.style = discord.ButtonStyle.gray  # Set the button style to gray

    @discord.ui.button(label="No", custom_id="nbutton", style=discord.ButtonStyle.green)
    async def nobutton_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback function for the 'No' button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button object.
        """
        if interaction.user.id == self.invoker_id:
            await self.disable_buttons()  # Disable all buttons in the view
            hp = self.player.determine_start_hp(self.dndclass)
            hp = int(hp)
            lvl = 1
            await interaction.response.edit_message(
                content=self.player.show_stats(
                    self.ctx, self.race_name, self.dndclass, lvl, hp
                ),
                view=self,
            )  # Edit the original message
            await self.ctx.channel.send(
                await self.player.save_to_csv(
                    self.character_name,
                    self.race_name,
                    self.ctx,
                    self.dndclass,
                    self.invoker_id,
                    lvl,
                    hp,
                )
            )
        else:
            await interaction.response.send_message(
                "This is not your decision to make. :point_up: :nerd:",
                ephemeral=True,
                delete_after=15,
            )  # Send an error message if someone else tries to click the button

    @discord.ui.button(label="Yes", custom_id="ybutton", style=discord.ButtonStyle.red)
    async def yesbutton_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback function for the 'Yes' button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button object.
        """
        if interaction.user.id == self.invoker_id:
            player = Character(
                self.character_name, self.ctx.guild.id
            )  # Create a Character object
            player.roll_stats(self.num_dice, self.sides)  # Roll character stats
            await self.disable_buttons()  # Disable all buttons in the view
            hp = player.determine_start_hp(self.dndclass)
            hp = int(hp)
            lvl = 1
            await interaction.response.edit_message(
                content=player.show_stats(
                    self.ctx, self.race_name, self.dndclass, lvl, hp
                ),
                view=self,
            )  # Edit the original message
            await self.ctx.channel.send(
                await player.save_to_csv(
                    self.character_name,
                    self.race_name,
                    self.ctx,
                    self.dndclass,
                    self.invoker_id,
                    lvl,
                    hp,
                )
            )  # Save character stats to CSV
        else:
            await interaction.response.send_message(
                "This is not your decision to make. :point_up: :nerd:",
                ephemeral=True,
                delete_after=15,
            )  # Send an error message if someone else tries to click the button

    async def on_timeout(self):
        """
        Handler for when the view times out.
        """
        await self.disable_buttons()  # Disable all buttons in the view
