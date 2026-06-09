import os
from dotenv import load_dotenv

load_dotenv()

# Fallback list of free public proxies to use for scraping when no PROXIES
# environment variable is provided. These are public proxies and may be
# unreliable; replace or extend them as needed.
DEFAULT_FREE_PROXIES = [
	"http://51.158.68.26:8811",
	"http://34.91.135.27:3128",
	"http://138.197.157.49:8080",
]

# Comma-separated proxy URLs (e.g. http://user:pass@host:port). If the
# `PROXIES` env var is not set, fall back to `DEFAULT_FREE_PROXIES`.
PROXIES = [p for p in os.getenv("PROXIES", "").split(",") if p] or DEFAULT_FREE_PROXIES

# Rate limit settings for Places API (calls per period)
RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "5"))
RATE_LIMIT_PERIOD = float(os.getenv("RATE_LIMIT_PERIOD", "1.0"))

# Go scraper API (used to submit jobs to Go workers)
GO_SCRAPER_API_URL = os.getenv("GO_SCRAPER_API_URL", "http://localhost:8080/api/v1")
GO_SCRAPER_API_KEY = os.getenv("GO_SCRAPER_API_KEY", "")