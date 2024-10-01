import os
from dotenv import load_dotenv

load_dotenv(".env")

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HUMAN_ICON = "👤"
AI_ICON = "🤖"


def load_config():
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        "HUMAN_ICON": HUMAN_ICON,
        "AI_ICON": AI_ICON,
    }
