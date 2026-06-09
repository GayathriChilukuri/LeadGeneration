import asyncio
from discovery.area_generator import generate_queries
from discovery.google_places import google_places_client


class DiscoveryService:

    def __init__(self, concurrency: int = 8):
        self._semaphore = asyncio.Semaphore(concurrency)

    async def _search_query(self, query: str):
        async with self._semaphore:
            print(f"Searching: {query}")
            try:
                companies = await google_places_client.search_single_query(query)
                return companies
            except Exception as ex:
                print(f"Failed query {query}: {ex}")
                return []

    async def discover_companies(self, industry: str, city: str):
        queries = generate_queries(industry=industry, city=city)

        tasks = [self._search_query(q) for q in queries]

        results = await asyncio.gather(*tasks)

        # flatten
        all_companies = [c for sub in results for c in sub]

        return all_companies


discovery_service = DiscoveryService()