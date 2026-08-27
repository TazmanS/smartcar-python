from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.post("/detect")
async def detect(file: UploadFile):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
    }
