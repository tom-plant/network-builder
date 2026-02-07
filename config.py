# config.py
# Configuration and API keys

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, try to load from environment directly
    pass

# API Keys - load from environment variables
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
CLAUDE_KEY = os.getenv("CLAUDE_KEY")

# Validate that keys are set
if not SERPAPI_KEY or SERPAPI_KEY == "your_serpapi_key_here":
    raise ValueError(
        "SERPAPI_KEY not set. Copy .env.example to .env and add your API key."
    )

if not CLAUDE_KEY or CLAUDE_KEY == "your_anthropic_api_key_here":
    raise ValueError(
        "CLAUDE_KEY not set. Copy .env.example to .env and add your API key."
    )

# Thresholds
ACCOUNT_THRESHOLD = 2  # Twitter, Facebook, Instagram, TikTok, YouTube
COMMUNITY_THRESHOLD = 2  # Reddit, Telegram

# Results
TOP_N_RESULTS = None  # No limit - return all accounts above threshold

# Rate limiting
SEARCH_DELAY = 0.5  # seconds between searches

# Safety limits for LLM-generated search strategies
MAX_PAGES_PER_BUNDLE = 10  # Maximum pages to fetch per keyword bundle
MAX_TOTAL_PAGES = 30       # Maximum total pages across all bundles
MIN_THRESHOLD = 2          # Minimum appearance threshold
MAX_THRESHOLD = 5          # Maximum appearance threshold

# News outlet exclusions (used when apply_filter=True)
NEWS_OUTLET_EXCLUSIONS = "-CNN -Reuters -BBCWorld -BBCNews -Bloomberg -AP -AFP -nytimes -washingtonpost -AlJazeera -MSNBC -FoxNews -CBSNews -ABCNews -NBCNews -NPR -Guardian -Independent -Telegraph"
