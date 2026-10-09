import os
from typing import Dict, List, Final
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# ==========================================
# ENV VARS & API KEYS
# ==========================================

# Required: The host to bind the Streamlit app to
APP_HOST: Final[str] = os.getenv("APP_HOST", "0.0.0.0")

# Required: The port to bind the Streamlit app to
APP_PORT: Final[int] = int(os.getenv("APP_PORT", "8501"))

# Optional: API key for specific scraping service if needed
SCRAPER_API_KEY: Final[str] = os.getenv("SCRAPER_API_KEY", "")

# ==========================================
# SCRAPER CONFIGURATION
# ==========================================

# Dict mapping generic site name to base URL
SCRAPER_TARGETS: Final[Dict[str, str]] = {
    "amazon": "https://www.amazon.com",
    "walmart": "https://www.walmart.com",
    "ebay": "https://www.ebay.com"
}

# Request headers to mimic a browser
DEFAULT_HEADERS: Final[Dict[str, str]] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# ==========================================
# UI & THEME CONSTANTS (Brutalism)
# ==========================================

# Primary color scheme
# Backgrounds, typography, accents
THEME_COLORS: Final[Dict[str, str]] = {
    "bg": "#000000",             # Solid Black
    "fg": "#FFFFFF",             # Pure White
    "accent": "#FF0000",         # Intense Red
    "secondary_accent": "#FFFF00", # Pure Yellow
    "surface": "#1A1A1A",        # Dark Gray
}

# Standard styling constants
BORDER_WIDTH: Final[str] = "3px"
BORDER_STYLE: Final[str] = f"{BORDER_WIDTH} solid {THEME_COLORS['fg']}"

# ==========================================
# BUSINESS LOGIC CONSTANTS
# ==========================================

# Default profit margin filter (percentage)
DEFAULT_MIN_MARGIN_PERCENT: Final[float] = 15.0

# Estimated shipping cost per unit if not scraped
DEFAULT_SHIPPING_COST: Final[float] = 5.00