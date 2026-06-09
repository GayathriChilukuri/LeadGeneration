Setup and Run
----------------

1. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3a. Install Playwright browsers

```bash
python -m playwright install
```

If using CI or Docker, ensure the Playwright browsers are installed and the container has required dependencies.

3. Environment variables

- `PROXIES` (optional): comma-separated proxy URLs. If not set, the app
  falls back to a small list of free public proxies defined in
  `core/config.py`.
- `GO_SCRAPER_API_URL`, `GO_SCRAPER_API_KEY`, and rate-limit env vars remain
  configurable as before.

4. Run the app (example for FastAPI)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Notes
-----
- The project no longer requires `GOOGLE_API_KEY`; scraping will use proxy
  requests instead of Google Places API. Public proxies are unreliable and
  may lead to IP bans — consider using a paid proxy or rotating proxy service
  for production.
