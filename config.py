import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'english_quest.db')}"
SECRET_KEY = os.getenv("SECRET_KEY")
APP_NAME = "English Quest"

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Dimer")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Session
SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"
SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", "604800"))  # 7 days

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Doubao TTS (Volcano Engine)
VOLC_APP_ID = os.getenv("VOLC_APP_ID")
VOLC_ACCESS_TOKEN = os.getenv("VOLC_ACCESS_TOKEN")

# SRS intervals (seconds): 1 day / 1 week / 1 month
SRS_INTERVALS = [86400, 604800, 2592000]
