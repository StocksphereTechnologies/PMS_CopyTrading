
import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.getcwd())

from app.services.account_service import AccountService
import logging

# Set up logging to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

async def run_init():
    print("Starting manual session initialization...")
    try:
        await AccountService.initialize_all_sessions()
        print("Manual session initialization finished.")
    except Exception as e:
        print(f"CRITICAL ERROR in manual init: {e}")

if __name__ == "__main__":
    asyncio.run(run_init())
