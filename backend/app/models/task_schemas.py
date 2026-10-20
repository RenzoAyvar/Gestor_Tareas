from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1, max_length=120)
    descripcion: str = Field(min_length=1, max_length=1000)
    fecha_limite: date | None = None

    @field_validator("titulo", "descripcion")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("El campo no puede contener solo espacios en blanco.")
        return value.strip()


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    completada: bool = Field(strict=True)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    titulo: str
    descripcion: str
    fecha_limite: date | None
    completada: bool
    creada_en: datetime


TaskStatus = Literal["all", "pending", "completed"]
