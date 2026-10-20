import re
from pydantic import BaseModel, Field, field_validator

class LoginRequest(BaseModel):
    correo: str = Field(min_length=1)
    password: str = Field(min_length=1)

    @field_validator("correo")
    @classmethod
    def reject_spaces(cls, value: str) -> str:
        if re.search(r"\s", value):
            raise ValueError("El correo no debe contener espacios en blanco.")
        return value

class LoginResponse(BaseModel):
    correo: str
    token: str
    token_type: str = "bearer"
