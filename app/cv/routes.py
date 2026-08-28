from fastapi import APIRouter, UploadFile

from app.cv.handler import detect_handler
from app.cv.schemas import DetectionResponse

router = APIRouter()


@router.post("/detect", response_model=DetectionResponse)
async def detect_route(file: UploadFile):
    return await detect_handler(file)
