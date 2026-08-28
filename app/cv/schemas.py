from pydantic import BaseModel


class Detection(BaseModel):
    class_name: str
    confidence: float
    left: float
    top: float
    right: float
    bottom: float


class DetectionResponse(BaseModel):
    objects: list[Detection]
