from pydantic import BaseModel


class Company(BaseModel):
    name: str

    website: str | None = None
    phone: str | None = None
    address: str | None = None

    email: str | None = None
    linkedin: str | None = None

    company_size: str | None = None