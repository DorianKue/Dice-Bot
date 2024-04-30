# Discord Dice-Roll Bot

## Introduction

This is a simple Discord bot, designed to roll dice. Optionally with modifiers. You can also roll for character stats, based on the DnD5e ruleset and save the stats with a given character

## Features

### Dice Rolling

- **Roll Any Number of Dice**: Users can roll any number of dice with any number of sides, along with an optional modifier.
- **Flexible Syntax**: The bot supports a flexible syntax for rolling dice, allowing users to specify the number of dice, sides, and modifier in a single command.

### Character Creation

- **Stat Generation**:  Users can roll stats for their characters using the !roll_char command, with the bot automatically calculating ability score modifiers based on the rolled stats according to DnD5e rules.
- **Character Naming**: After rolling stats, users are prompted to enter a name for their character.

### Character Management

- **Display Character Stats**: Users can view the stats of their created characters using the `!stats` command. Stats are displayed in a tabulated format for easy readability.
- **Remove Character Savefiles**: Users with appropriate permissions can delete the savefiles of characters using the `!rm` command. This feature helps manage the server's storage space by allowing users to clean up unnecessary files.

### Customizable Prefix

- **Flexible Command Prefix**: The bot allows users to use either `!` or `/` as the command prefix, providing flexibility and compatibility with different server setups.

## Planned features

### Character Sheet Management
Character Sheet Management: Allow users to edit character sheets directly within Discord. This feature could include commands for modifying existing stats, adding new stats, setting up character backgrounds, and more.

### Dice Rolling Options
Expand the dice rolling functionality to support more complex rolls, such as rolling with advantage/disadvantage

### Server-Specific Settings 
Allow server administrators to customize bot settings and permissions on a per-server basis. This could include setting command prefixes, defining access levels for certain commands, and configuring logging or moderation features.

### Error Handling and Feedback
Implement robust error handling and provide informative feedback messages when users input invalid commands or encounter errors


## Installation

1. **Python Version**: Ensure you have Python version 3.xx or higher installed on your system. If not, you can download and install it from the [official Python website](https://www.python.org/downloads/).


2. **Clone the Repository**: Clone the repository to your local machine using the following command:
git clone https://github.com/DorianKue/dice-roll-bot.git


3. **Install Dependencies**: Navigate to the project directory and install the required Python packages using pip:
pip install -r requirements.txt


4. **Configure Environment Variables**: Create a `.env` file in the root directory and add your Discord bot token as follows:
DISCORD_TOKEN=your_token_here


5. **Run the Bot**: Execute the `bot_main.py` script to start the bot:
python bot_main.py


## Usage

### Commands

- **Rolling Dice**: Use the `!roll` command to roll dice with the specified parameters. Example: `!roll 2d6+3`.
- **Creating Characters**: Use the `!roll_char` command to roll stats for a character. Example: `!roll_char 4d6`.
- **Displaying Character Stats**: Use the `!stats` command to display character stats. Example: `!stats Bob`.
- **Removing Character Savefile**: Use the `!rm` command to remove a character savefile. Example: `!rm Bob`.

### Prefix

You can use either `!` or `/` as the command prefix. For example, both `!roll 2d6` and `/roll 2d6` will work.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/licenses/MIT) file for details.

## Support

For support, bug reports, or feature requests, please [open an issue](https://github.com/DorianKue/dice-roll-bot/issues) on GitHub.