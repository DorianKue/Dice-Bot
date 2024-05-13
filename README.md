# Discord Dice-Roll Bot

## Introduction

A Discord bot, designed to roll dice. Optionally with modifiers. 
You can also roll a character, including race and class or get a randomly created character, based on the DnD5e ruleset and save the stats.
Furthermore you can level them up and choose which method you want to use to increase their HP. Either roll for it using your classes hit dice or take the average.


## Features

### Dice Rolling

- **Roll Any Number of Dice**: Users can roll any number of dice with any number of sides, along with an optional modifier.
- **Flexible Syntax**: The bot supports a flexible syntax for rolling dice, allowing users to specify the number of dice, sides, and modifier in a single command.

### Character Creation

-**Class and Race options**: Before rolling for stats you can choose your characters class and race, based on DnD.

- **Stat Generation**:  Users can roll stats for their characters using the /roll_char command, with the bot automatically calculating ability score modifiers based on the rolled stats according to DnD5e rules.


### Character Management

- **Display Character Stats**: Users can view the stats of their created characters using the `/stats` command. Stats are displayed in a tabulated format for easy readability. This includes the characters name, race, class, and level.
- **Level a Character**: Using the `/lvl` command, users can level up their characters. This increases their health based on the characters class. Before doing that, the bot prompts the user which way they prefer to increase their HP. Take a risk by rolling, using their hit dice or take the average. You get prompted every time to leave options open.
- **Show all Characters**: The `/showall`command shows all characters currently saved on the server. Includes their names, race, class and level.
- **Remove Character Savefiles**: Users with appropriate permissions can delete the savefiles of characters using the `/rm` command. This feature helps manage the server's storage space by allowing users to clean up unnecessary files.

### Customizable Prefix

- **Flexible Command Prefix**: The bot uses `slash commands` but also  allows admins to set a custom prefix using the `/setprefix` command, providing flexibility and compatibility with different server setups.

### Other features

- **Random**: `/random` command can be used to get a random number between 1 and X - with X being the user input. However you can also specify the start, by using the command like so: `/random 50-100`- this would return a random number between 50 and 100.

- **Coinflip**: Pretty self explanatory. Flips a coin for you.


## Installation

1. **Python Version**: Ensure you have Python version 3.xx or higher installed on your system. If not, you can download and install it from the [official Python website](https://www.python.org/downloads/).


2. **Clone the Repository**: Clone the repository to your local machine using the following command:
git clone https://github.com/DorianKue/dice-roll-bot.git


3. **Install Dependencies**: Navigate to the project directory and install the required Python packages using pip:
pip install -r requirements.txt


4. **Configure Environment Variables**: Create a `.env` file in the root directory and add your Discord bot token inside the `.env` file as follows:
DISCORD_TOKEN=your_token_here


5. **Run the Bot**: Execute the `bot_main.py` script to start the bot:
python bot_main.py


## Usage

### Commands

- **Help Command**: The `/help` command shows a full list of commands.
- **Rolling Dice**: `/roll` command allows you to roll dice with the specified parameters. Example with modifier: `/roll 2d6+3` - Modifier can be negative. - No modifier: `/roll 2d6`.
- **Creating Characters**: Use the `/roll_char` command to create a character. Includes race and class selection. Example: `/roll_char 4d6 Bob`- Command excludes the lowest roll for stats.
- **Create a random Character**: The `random_char`command gives you a character with a random class and race and stats rolled with 4d6. Example: `/random_char Bob`.
- **Displaying Character Stats**: Use the `/stats` command to display character stats. Example: `/stats Bob`.
- **Displaying all Characters**: Simply type `/showall`.
- **Leveling a Character**: Type `/lvl` followed by the name of your character to increase its health and if applicable gain attribute points to spend. Example `/lvl Bob`.
- **Removing Character Savefile**: `/rm` command to remove a character savefile. Example: `/rm Bob`.
- **Random number**: This command allows you to get a random number. Either from a specified range `/random 50-100` for example, or starting at 1. `/random 100` - this returns a number between 1 and 100.
- **Coinflip**: `/coinflip`
- **Set a custom prefix**: If you have admin privileges you can use the `/setprefix`command to set a custom prefix. Example: `/setprefix !` - now you can use ! together with / as a prefix.
    - Note: Only **ONE** custom prefix can be set. `/` is always available.
-**Remove custom prefix**: If you want to remove your previously set custom prefix and have admin privileges, simply use `/rmprefix`.



## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/licenses/MIT) file for details.

## Support

For support, bug reports, or feature requests, please [open an issue](https://github.com/DorianKue/dice-roll-bot/issues) on GitHub.