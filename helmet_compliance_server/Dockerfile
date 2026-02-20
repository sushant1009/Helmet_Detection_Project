FROM python:3.10-alpine

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    cmake \
    gcc \
    g++ \
    gfortran \
    openblas-dev \
    linux-headers

# Install runtime dependencies
RUN apk add --no-cache \
    libstdc++ \
    glib \
    libgomp

RUN python -m venv .venv

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir onnxruntime>=1.15.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]