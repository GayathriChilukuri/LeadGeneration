import requests

from core.config import GOOGLE_API_KEY


TEXT_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchText"
)

PLACE_DETAILS_URL = (
    "https://places.googleapis.com/v1/places"
)


class GooglePlacesClient:

    def __init__(self):
        self.api_key = GOOGLE_API_KEY

    def search_single_query(
        self,
        query: str
    ):

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress"
            )
        }

        payload = {
            "textQuery": query
        }

        response = requests.post(
            TEXT_SEARCH_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        companies = []

        for place in data.get("places", []):

            company = {
                "place_id": place.get("id"),
                "name": place.get(
                    "displayName",
                    {}
                ).get("text"),
                "address": place.get(
                    "formattedAddress"
                ),
                "website": None,
                "phone": None
            }

            try:

                details = self.get_place_details(
                    company["place_id"]
                )

                company["website"] = (
                    details["website"]
                )

                company["phone"] = (
                    details["phone"]
                )

            except Exception as e:

                print(
                    f"Error fetching details "
                    f"for {company['name']}: {e}"
                )

            companies.append(company)

        return companies

    def get_place_details(
        self,
        place_id: str
    ):

        url = (
            f"{PLACE_DETAILS_URL}/{place_id}"
        )

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "websiteUri,"
                "nationalPhoneNumber"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return {
            "website": data.get(
                "websiteUri"
            ),
            "phone": data.get(
                "nationalPhoneNumber"
            )
        }


google_places_client = (
    GooglePlacesClient()
)