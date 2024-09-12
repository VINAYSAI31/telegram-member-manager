

## Installation

### Prerequisites

- Python 3.x
- Flask
- Telethon (or any other Telegram API library you use)

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/telegram-bot-project.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd telegram-bot-project
   ```

3. **Set up a virtual environment:**

   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

5. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables:**

   Create a `.env` file in the root directory and add your Telegram API credentials:

   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   ```

7. **Set up your base file path:**

   - Open the `routes.py` file.
   - Locate the global variable `BASE_FILE_PATH` at the top of the file.
   - Replace the placeholder path with the actual directory path where you want to save the CSV files. For example:

     ```python
     # Define a global variable for the base file path
     BASE_FILE_PATH = 'C:\\path\\to\\your\\directory'
     ```

   Make sure this directory exists on your system and is writable by the application.

## Usage

### Running the Flask Application

To start the Flask web application, run:

```bash
python app.py
```

### Interacting with the Bot

1. **Open the web application** in your browser (typically `http://127.0.0.1:5000`).
2. **Enter the group ID** and desired ID pattern in the provided fields.
3. **Click 'Run Bot'** to fetch and filter users.

The bot will:
- Fetch users from the specified group.
- Filter users based on the provided ID pattern.
- Generate CSV files containing user details.

### CSV Files

- `all_members.csv`: Contains details of all users in the group.
- `correct_usernames.csv`: Contains details of users with IDs matching the pattern.
- `removed_users.csv`: Contains details of users removed from the group.

## Contributing

1. **Fork the repository.**
2. **Create a new branch:**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Make your changes and commit:**

   ```bash
   git commit -am 'Add new feature'
   ```

4. **Push to the branch:**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Create a new Pull Request.**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Telegram API for providing the bot functionality.
- Special thanks to the Flask and Telethon communities for their support and libraries.

