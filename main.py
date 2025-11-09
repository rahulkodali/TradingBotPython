import os
import asyncio
from manager.positionManager import PositionManager
from streamers.streamingData import EMAEngine

if __name__ == "__main__":
    # from dotenv import load_dotenv - will set up .env file later
    # load_dotenv()

    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("SECRET_API_KEY")

    pm = PositionManager()
    pm.initialize()

    engine = EMAEngine(pm)
    asyncio.run(engine.run())