import cv2
import numpy as np
from fastapi import UploadFile
from ultralytics import YOLO

model = YOLO("yolo11n.pt")


async def detect_service(file: UploadFile):
    image = await file.read()

    image_array = np.frombuffer(image, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    results = model(image)

    result = results[0]

    objects = []

    image_height, image_width = image.shape[:2]

    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        objects.append(
            {
                "class": model.names[class_id],
                "confidence": confidence,
                "left": x1 / image_width,
                "top": y1 / image_height,
                "right": x2 / image_width,
                "bottom": y2 / image_height,
            }
        )

    return {
        "objects": objects,
    }
