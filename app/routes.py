from fastapi import APIRouter

from app.cv.routes import router as cv_router

router = APIRouter(prefix="/api")

router.include_router(cv_router)
