import os
import time
from typing import Optional

import httpx

from core.config import GO_SCRAPER_API_URL, GO_SCRAPER_API_KEY
from discovery.area_generator import generate_queries


DEFAULT_TIMEOUT = 30


class JobProducer:

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, rate_delay: float = 0.2):
        self.api_url = api_url or GO_SCRAPER_API_URL
        self.api_key = api_key or GO_SCRAPER_API_KEY
        self.rate_delay = rate_delay

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            # prefer Authorization Bearer, fallback to X-API-Key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def submit_keyword(self, keyword: str, timeout: int = 300, lang: str = "en", max_depth: int = 1, email: bool = False, fast_mode: bool = False):
        url = f"{self.api_url.rstrip('/')}/scrape"
        payload = {
            "keyword": keyword,
            "lang": lang,
            "max_depth": max_depth,
            "email": email,
            "fast_mode": fast_mode,
            "timeout": timeout,
        }

        headers = self._headers()

        resp = httpx.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()

        return resp.json()

    def produce_jobs_for_industry(self, industry: str, city: str, max_jobs: Optional[int] = None):
        queries = generate_queries(industry=industry, city=city)

        submitted = []

        for i, q in enumerate(queries):
            if max_jobs and i >= max_jobs:
                break

            try:
                res = self.submit_keyword(q)
                submitted.append({"query": q, "response": res})
            except Exception as e:
                submitted.append({"query": q, "error": str(e)})

            # small delay to avoid hammering the API
            time.sleep(self.rate_delay)

        return submitted


if __name__ == "__main__":
    # simple CLI for local use
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("industry")
    parser.add_argument("city")
    parser.add_argument("--api-url", help="Go scraper API URL")
    parser.add_argument("--api-key", help="Go scraper API key")
    parser.add_argument("--max", type=int, help="Max jobs to produce")
    args = parser.parse_args()

    producer = JobProducer(api_url=args.api_url, api_key=args.api_key)
    out = producer.produce_jobs_for_industry(args.industry, args.city, max_jobs=args.max)

    for item in out:
        print(item)
