import logging
import os

from bot.bot import Bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)


def main():
    # Create a Discord bot instance (with Discord initialized)
    bot = Bot(initialize_discord=True)
    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
