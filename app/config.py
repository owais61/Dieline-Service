import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Dieline Generator Service")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
