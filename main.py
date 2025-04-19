import logging
import os
import threading

import uvicorn

from bot.bot import Bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)


def run_fastapi(bot: Bot):
    uvicorn.run(bot.web_app, host="0.0.0.0", port=8000)


def main():
    bot = Bot()

    # Run FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi, args=(bot,))
    fastapi_thread.start()

    bot.run(os.getenv("TOKEN"))


if __name__ == "__main__":
    main()
