import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "URJA_BASE_URL",
    "https://urja-ops.flockenergy.tech",
)

EMAIL = os.getenv("URJA_EMAIL")
PASSWORD = os.getenv("URJA_PASSWORD")