HYDERABAD_AREAS = [
    "gachibowli",
    "hitech city",
    "madhapur",
    "kondapur",
    "jubilee hills",
    "banjara hills",
    "kukatpally",
    "manikonda",
    "financial district",
    "begumpet",
    "ameerpet",
    "secunderabad",
    "lb nagar",
    "uppal",
    "kompally",
    "nallagandla",
    "tellapur",
    "miyapur",
    "chandanagar",
    "shamshabad"
]


SEARCH_PATTERNS = [
    "{industry} {area} {city}",
    "{industry} company {area} {city}",
    "{industry} agency {area} {city}",
    "{industry} services {area} {city}",
    "{industry} firms {area} {city}"
]


def generate_queries(
    industry: str,
    city: str
):

    queries = []

    for area in HYDERABAD_AREAS:

        for pattern in SEARCH_PATTERNS:

            query = pattern.format(
                industry=industry,
                area=area,
                city=city
            )

            queries.append(query)

    return queries