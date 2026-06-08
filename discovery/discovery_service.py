from discovery.area_generator import generate_queries
from discovery.google_places import google_places_client


class DiscoveryService:

    def discover_companies(
        self,
        industry: str,
        city: str
    ):

        queries = generate_queries(
            industry=industry,
            city=city
        )

        all_companies = []

        for query in queries:

            print(f"Searching: {query}")

            try:

                companies = (
                    google_places_client
                    .search_single_query(query)
                )

                all_companies.extend(companies)

            except Exception as ex:

                print(
                    f"Failed query "
                    f"{query}: {ex}"
                )

        return all_companies


discovery_service = DiscoveryService()