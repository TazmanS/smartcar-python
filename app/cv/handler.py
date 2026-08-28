from fastapi import UploadFile

from app.cv.service import detect_service


async def detect_handler(file: UploadFile):
    return await detect_service(file)
