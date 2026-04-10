FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV INSIGHTFACE_HOME=/root/.insightface  

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    build-essential \
    libopenblas-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app
WORKDIR /app

EXPOSE 8003

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "1"]