from discovery.discovery_service import discovery_service


def generate_leads(
    industry: str,
    city: str,
    count: int = 500
):

    companies = discovery_service.discover_companies(
        industry=industry,
        city=city
    )

    return {
        "requested_count": count,
        "returned_count": len(companies),
        "companies": companies[:count]
    }