# config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.game_entities import Base  # Assuming Base is defined in models/game_entities.py

# Static connection string for Render.com PostgreSQL
DATABASE_URL = "postgresql://epsilon_51hw_user:odXXC7QP1IpBhOQTAjdBs5uksmiufu6H@dpg-cvmm76vfte5s738rpks0-a/epsilon_51hw"

# Folder paths for asset management
ASSET_PATHS = {
    "portraits": "assets/portraits/",
    "backstories": "assets/backstories/",
}

# Create the engine
engine = create_engine(DATABASE_URL, echo=True)

# Create the sessionmaker for working with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the database
def init_db():
    """Initialize the database by creating all tables."""
    try:
        # Create the tables in the database
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
