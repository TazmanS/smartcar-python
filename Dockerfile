FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
  torch \
  torchvision \
  --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt \
  && pip uninstall -y opencv-python \
  && pip install --no-cache-dir opencv-python-headless

COPY app ./app
COPY yolo11n.pt .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]