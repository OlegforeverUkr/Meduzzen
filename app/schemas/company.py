from app.utils.visability import VisibilityEnum
from pydantic import BaseModel, field_validator
from app.schemas.users import UserSchema


MIN_LEN = 5


class CompanySchema(BaseModel):
    id: int
    company_name: str
    description: str
    owner: UserSchema
    visibility: VisibilityEnum


class CompanyCreateSchema(BaseModel):
    company_name: str
    description: str
    visibility: VisibilityEnum

    class Config:
        from_attributes = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "company_name": "company name",
                "description": "description of company",
                "visibility": "'public' or 'private'"
            }
        }

    @classmethod
    @field_validator("company_name",  "description", mode="before")
    def validate_fields(cls, company_name, description):
        validated_company_name = company_name.replace(" ", "")
        validated_description = description.replace(" ", "")
        if len(company_name) < MIN_LEN or len(description) < MIN_LEN:
            raise ValueError('Company name and description must contain at least 5 characters')
        return validated_company_name, validated_description



class CompanyUpdateSchema(BaseModel):
    company_name: str | None = None
    description: str | None = None
    visibility: VisibilityEnum | None = None

    class Config:
        from_attributes = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "company_name": "company name",
                "description": "description of company",
                "visibility": "'public' or 'private'"
            }
        }

    @classmethod
    @field_validator("company_name",  "description", mode="before")
    def validate_fields(cls, company_name, description):
        company_name = company_name.replace(" ", "")
        description = description.replace(" ", "")
        if len(company_name) < MIN_LEN or len(description) < MIN_LEN:
            raise ValueError('Company name and description must contain at least 5 characters')
        return company_name, description