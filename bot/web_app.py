import logging

from dotenv import load_dotenv

from bot.bot import Bot
from bot.discord_client import get_discord_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("web_app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize the shared Discord client early
try:
    get_discord_client()
    logger.info("Discord client initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Discord client: {e}")

# Create an instance of the bot for the web app
bot = Bot(initialize_discord=False)

# Export the FastAPI app for Gunicorn
app = bot.web_app


# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
