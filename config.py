# config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Explicitly ensure using the same Base object

DATABASE_URL = "postgresql://epsilon_51hw_user:odXXC7QP1IpBhOQTAjdBs5uksmiufu6H@dpg-cvmm76vfte5s738rpks0-a/epsilon_51hw"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Explicit WebSocket timeout parameter (in seconds)
WEBSOCKET_INACTIVITY_TIMEOUT = 600  # 10 minutes

