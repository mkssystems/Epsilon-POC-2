from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env in root directory

DATABASE_URL = os.getenv("DATABASE_URL")
ASSET_PATHS = {
    "portraits": "assets/portraits/",
    "backstories": "assets/backstories/",
}
