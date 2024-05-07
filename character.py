import random
from tabulate import tabulate
import os
import csv


class Character:
    """Represents a character with stats."""

    def __init__(self, name, server_id):
        """Initialize a Character object."""
        self.name = name  # Assign the name of the character
        self.stats = {  # Initialize character stats dictionary
            "Strength": 0,
            "Dexterity": 0,
            "Intelligence": 0,
            "Constitution": 0,
            "Charisma": 0,
            "Wisdom": 0,
        }
        self.ability_score_modifier = {}  # Initialize ability score modifier dictionary
        self.server_id = server_id

    def roll_stats(self, num_dice, sides):
        """Roll the character's stats based on the number of dice and sides."""
        for stat in self.stats:  # Iterate through each stat
            self.stats[stat] = self.determine_stats(
                num_dice, sides
            )  # Roll the dice and assign the result to the stat
            self.calculate_modifier()  # Calculate the modifier for the rolled stats

    def determine_stats(self, num_dice, sides):
        """Determine the stats by rolling the dice."""
        rolls = [
            random.randint(1, sides) for _ in range(num_dice)
        ]  # Roll the dice specified number of times
        rolls.sort()  # Sort the rolls in ascending order
        if num_dice > 1:
            return sum(rolls[1:])  # Sum the rolls excluding the lowest roll
        else:
            return sum(rolls)

    def calculate_modifier(self, stat_value=None):
        """Calculate the ability score modifiers."""
        if stat_value is None:
            # Calculate modifiers for all stats
            for (
                stat_name,
                stat_value,
            ) in self.stats.items():  # Iterate through each stat
                modifier = (stat_value - 10) // 2  # Calculate the modifier
                self.ability_score_modifier[stat_name] = (
                    modifier  # Assign the modifier to the stat
                )
        else:
            # Calculate modifier for a specific stat
            modifier = (stat_value - 10) // 2  # Calculate the modifier
            return modifier  # Return the calculated modifier

    def show_stats(self, ctx, race_name):
        """Display the character's stats."""
        table = []  # Initialize an empty list for the table
        for key, value in self.stats.items():  # Iterate through each stat
            modifier = self.ability_score_modifier.get(
                key, 0
            )  # Get the modifier for the stat
            if modifier >= 1:  # Check if modifier is non-negative
                modifier_str = f"+{modifier}"  # Format modifier string with a plus sign
            else:
                modifier_str = str(modifier)  # Convert modifier to string
            table.append(
                [key, value, modifier_str]
            )  # Append stat, value, and modifier to the table
        headers = ["Attribute", "Value", "Modifier", "Race"]  # Define table headers
        stats_table = tabulate(
            table, headers=headers, tablefmt="grid"
        )  # Format table using tabulate
        return f"Race: {race_name}\n```{stats_table}```"  # return the formatted table to Discord

    async def save_to_csv(self, char_name, race_name, ctx):
        """
        Save the character's stats to a CSV file.

        Args:
            char_name (str): The name of the character.
            ctx: The context object representing the invocation context.
        """
        try:
            # Construct directory path based on server ID
            server_dir = f"server_{self.server_id}"
            # Ensure the directory exists, if not, create it
            os.makedirs(server_dir, exist_ok=True)
            # Define the filename based on character name
            filename = f"{char_name}_stats.csv"
            # Construct the full file path
            filepath = os.path.join(server_dir, filename)
            # Check if the file already exists
            file_exists = os.path.isfile(filepath)
            # Open the file in append mode if it exists, otherwise in write mode - For now only in write mode. Don't want to append but left it in, in case i need it.
            with open(filepath, "w" if file_exists else "w", newline="") as file:
                # Define field names for CSV header
                fieldnames = ["Name", "Race", "Attribute", "Value", "Modifier"]
                # Initialize CSV DictWriter
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                # Write header if the file is newly created
                if not file_exists:
                    writer.writeheader()
                # Iterate through character stats
                for key, value in self.stats.items():
                    # Get the modifier for the current attribute
                    modifier = self.ability_score_modifier.get(key, 0)
                    # Write a row to the CSV file
                    writer.writerow(
                        {
                            "Name": char_name,
                            "Race": race_name,
                            "Attribute": key,
                            "Value": value,
                            "Modifier": modifier,
                        }
                    )
            # Send confirmation message
            # await ctx.channel.send("Character stats have been saved.")
            return "Character stats have been saved."
        except Exception as e:
            # Send error message if an exception occurs
            await ctx.send(
                f"An error occurred while trying to save: {e}", ephemeral=True
            )

    @staticmethod
    async def display_character_stats(ctx, char_name, server_id):
        """
        Display the character's stats in a tabulated format.

        Args:
            ctx: The context object representing the invocation context.
            char_name (str): The name of the character.
            server_id: The ID of the server where the character belongs.

        Returns:
            discord.Message: The message object containing the displayed stats.
        """
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
                name = None
                race_name = None
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
                    if race_name is None:
                        race_name = row["Race"]  # Finding race of the character
                    if name is None:
                        name = row["Name"]  # Finding name of the character
                # If CSV file is empty or only contain headers, send an error message
                if not stats:
                    await ctx.send(
                        f"'{char_name}' savefile seems to be empty. :confused:"
                    )
                    return None
                # Define headers for the tabulated output
                headers = ["Attribute", "Value", "Modifier"]
                # Generate a tabulated representation of the stats
                stats_table = tabulate(stats, headers=headers, tablefmt="grid")
                name_display = f"`Name`: {name}" if name else ""
                race_display = f"`Race`: {race_name}\n" if race_name else ""
                # Send the name, race and tabulated stats to the Discord channel and store the message object
                message = await ctx.send(
                    f"{name_display}  {race_display}```{stats_table}```"
                )
                # Return the message object
                return message
        except FileNotFoundError:
            await ctx.send(
                f"'{char_name}' savefile not found.", ephemeral=True, delete_after=120
            )
        except Exception as e:
            # Send error message if an exception occurs
            await ctx.send(f"An error occurred: {e}", ephemeral=True)
            return None  # Return None if an error occurs

    @classmethod
    async def update_character_stat(cls, ctx, name, selected_stat):
        # Construct directory path based on server ID
        server_dir = f"server_{ctx.guild.id}"
        # Construct the full file path
        filepath = os.path.join(server_dir, f"{name}_stats.csv")

        # Read character stats from the CSV file
        with open(filepath, newline="") as file:
            reader = csv.DictReader(file)
            stats = list(reader)

        # Find the corresponding stat
        for stat in stats:
            if stat["Attribute"] == selected_stat:
                # Update the stat value
                stat["Value"] = str(int(stat["Value"]) + 1)
                # Calculate the new modifier using the instance method
                new_modifier = Character(name, ctx.guild.id).calculate_modifier(
                    int(stat["Value"])
                )
                # Update the modifier
                stat["Modifier"] = str(new_modifier)
                break

        # Write the updated stats back to the file
        with open(filepath, "w", newline="") as file:
            fieldnames = ["Name", "Race", "Attribute", "Value", "Modifier"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(stats)
