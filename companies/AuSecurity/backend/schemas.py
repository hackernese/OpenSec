from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum


class ServiceInterest(str, Enum):
    grc = "GRC Consulting"
    pentest = "Penetration Testing"
    not_sure = "Not Sure"


class ContactFormRequest(BaseModel):
    full_name: str
    company_name: str
    email: EmailStr
    phone: Optional[str] = None
    service_interest: ServiceInterest
    message: str
    h: str

    @field_validator("full_name", "company_name", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("This field cannot be empty")
        return v.strip()


class ContactFormResponse(BaseModel):
    success: bool
    message: str
    redirect_url: Optional[str] = None
    user_name: Optional[str] = None
    company_name: Optional[str] = None
