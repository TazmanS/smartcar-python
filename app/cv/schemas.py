from pydantic import BaseModel, Field


class Detection(BaseModel):
    class_: str = Field(alias="class")
    confidence: float
    left: float
    top: float
    right: float
    bottom: float


class DetectionResponse(BaseModel):
    objects: list[Detection]
