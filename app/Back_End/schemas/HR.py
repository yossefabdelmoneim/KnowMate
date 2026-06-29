from pydantic import BaseModel


class HRRequest(BaseModel):
    company_id: str
    question: str


class HRResponse(BaseModel):
    answer: str
    source: list[str] = []