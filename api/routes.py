from fastapi import APIRouter

from services.lead_generation_service import (
    generate_leads
)

router = APIRouter()


@router.post("/generate-leads")
def generate(
    industry: str,
    city: str,
    count: int = 500
):

    return generate_leads(
        industry=industry,
        city=city,
        count=count
    )