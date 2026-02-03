---
title: Face Embeddings Generator

sdk: docker
pinned: true
license: mit
---

# Face Embeddings Generator API

A FastAPI-based service that generates face embeddings using **InsightFace (buffalo_l)** model. Designed for worker and supervisor face verification workflows.

---

## Features

- **Face Detection** — Detects faces in uploaded images
- **Embedding Generation** — Generates normalized 512-d face embedding vectors

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/get-embeddings` | Generate face embedding from image |


---

## 📤Usage

### Generate Embeddings
```python
import requests

url = "https://sushant1004-face-embeddings-generator.hf.space"

with open("image.jpg", "rb") as img:
    response = requests.post(
        f"{url}/get-embeddings",
        files={"file": img}
    )

print(response.json())
```

**Response:**
```json
{
    "embedding": [0.123, -0.456, ...]
}
```


### Using cURL
```bash
# Get embeddings
curl -X POST "https://sushant1004-face-embeddings-generator.hf.space/get-embeddings" \
  -F "file=@image.jpg" \

```

---

## Tech Stack

- **Python 3.10**
- **FastAPI** — API Framework
- **InsightFace** — Face detection & recognition (buffalo_l model)
- **ONNX Runtime** — Model inference
- **OpenCV** — Image processing
- **NumPy** — Numerical computing

---

## Project Structure
```
├── app.py              # FastAPI application & endpoints
├── Dockerfile          # Docker container setup
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Environment

| Variable | Value |
|----------|-------|
| INSIGHTFACE_HOME | /root/.insightface |
| Port | 7860 |
| Workers | 1 |
| Model | buffalo_l |

---

## Requirements
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
insightface==0.7.3
opencv-python-headless==4.9.0.80
numpy==1.24.3
onnxruntime==1.17.0
Pillow==10.2.0
```

---

## Notes

- The model (`buffalo_l`) is pre-downloaded during Docker build to avoid runtime timeout
- Embeddings are **normalized** (unit vectors) so cosine similarity = dot product
- Similarity threshold for `same_person` is set to **0.6** — adjust as needed
- Currently runs on **CPU only**. For faster inference, upgrade to GPU hardware on Hugging Face

---


```
##
```
face-embeddings-generator/
├── app.py
├── Dockerfile
├── requirements.txt
└── README.md