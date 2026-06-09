import asyncio
import random
import re
import urllib.parse
from typing import List, Optional

from playwright.async_api import async_playwright, Error as PlaywrightError

from core.config import PROXIES


class ProxyManager:
    def __init__(self, proxies: List[str]):
        self._all = list(proxies)
        self._available = list(proxies)
        self._blacklist = {}

    def pick(self) -> Optional[str]:
        now = asyncio.get_event_loop().time()
        # cleanup expired
        expired = [p for p, t in self._blacklist.items() if t <= now]
        for p in expired:
            del self._blacklist[p]
            if p not in self._available:
                self._available.append(p)

        if not self._available:
            return None
        return random.choice(self._available)

    def mark_bad(self, proxy: str, ttl: int = 300):
        if not proxy:
            return
        try:
            self._available.remove(proxy)
        except ValueError:
            pass
        self._blacklist[proxy] = asyncio.get_event_loop().time() + ttl


proxy_manager = ProxyManager(PROXIES)


class GooglePlacesClient:
    """Headless Playwright-based Google Maps scraper with proxy rotation.

    Methods:
    - `search_single_query(query, max_results)` returns a list of place dicts
      with `place_url` and `name`.
    - `get_place_details(place_url)` returns `website` and `phone`.
    """

    def __init__(self):
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )

    async def _with_playwright(self, proxy: Optional[str]):
        pw = await async_playwright().start()
        launch_args = {"headless": True}
        if proxy:
            launch_args["proxy"] = {"server": proxy}
        browser = await pw.chromium.launch(**launch_args)
        return pw, browser

    async def search_single_query(self, query: str, max_results: int = 200) -> List[dict]:
        attempts = 0
        results: List[dict] = []
        while attempts < 6 and len(results) < max_results:
            proxy = proxy_manager.pick()
            pw = browser = None
            try:
                pw, browser = await self._with_playwright(proxy)
                context = await browser.new_context(user_agent=self.user_agent)
                page = await context.new_page()
                url = "https://www.google.com/maps/search/" + urllib.parse.quote(query)
                await page.goto(url, timeout=60000)
                # wait for results to appear
                try:
                    await page.wait_for_selector('a[href*="/place/"]', timeout=15000)
                except Exception:
                    pass

                # Scroll the results region to load more entries
                for _ in range(8):
                    await page.evaluate("window.scrollBy(0, 1000)")
                    await asyncio.sleep(0.6)

                anchors = await page.query_selector_all('a[href*="/place/"]')
                seen = set()
                for a in anchors:
                    href = await a.get_attribute("href")
                    if not href:
                        continue
                    # normalize URL
                    if href.startswith("/"):
                        full = "https://www.google.com" + href
                    else:
                        full = href
                    if "/place/" not in full:
                        continue
                    if full in seen:
                        continue
                    seen.add(full)
                    name = (await a.inner_text()) or None
                    results.append({"place_url": full, "name": name})
                    if len(results) >= max_results:
                        break

                await context.close()
                await browser.close()
                await pw.stop()
                if results:
                    return results
                attempts += 1
            except PlaywrightError:
                proxy_manager.mark_bad(proxy)
                attempts += 1
                try:
                    if browser:
                        await browser.close()
                    if pw:
                        await pw.stop()
                except Exception:
                    pass
                await asyncio.sleep(1 * attempts)
        return results

    async def get_place_details(self, place_url: str) -> dict:
        attempts = 0
        while attempts < 4:
            proxy = proxy_manager.pick()
            pw = browser = None
            try:
                pw, browser = await self._with_playwright(proxy)
                context = await browser.new_context(user_agent=self.user_agent)
                page = await context.new_page()
                await page.goto(place_url, timeout=60000)
                await asyncio.sleep(1.0)
                # Extract website: look for external links
                links = await page.query_selector_all('a[href^="http"]')
                website = None
                for l in links:
                    href = await l.get_attribute("href")
                    if href and "google.com" not in href:
                        website = href
                        break

                # Extract phone via regex from visible text
                visible = await page.inner_text("body")
                phone_match = re.search(r"(\+?\d[\d\-() ]{7,}\d)", visible)
                phone = phone_match.group(1) if phone_match else None

                await context.close()
                await browser.close()
                await pw.stop()
                return {"website": website, "phone": phone}
            except PlaywrightError:
                proxy_manager.mark_bad(proxy)
                attempts += 1
                try:
                    if browser:
                        await browser.close()
                    if pw:
                        await pw.stop()
                except Exception:
                    pass
                await asyncio.sleep(0.5 * attempts)
        return {"website": None, "phone": None}


google_places_client = GooglePlacesClient()