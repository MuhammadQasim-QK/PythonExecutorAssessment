FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    make \
    g++ \
    libprotobuf-dev \
    protobuf-compiler \
    libnl-route-3-dev \
    pkg-config \
    flex \
    bison \
    libc6-dev \
    linux-libc-dev \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git /tmp/nsjail \
    && cd /tmp/nsjail \
    && make \
    && mv nsjail /usr/local/bin/ \
    && rm -rf /tmp/nsjail

RUN pip install --no-cache-dir \
    flask \
    pandas \
    numpy

WORKDIR /app

COPY app.py /app/
COPY requirements.txt /app/
COPY nsjail.config.proto /app/

# Created a non-root user for security (but keep root for nsjail)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Keep root user for nsjail to work properly just uncomment the next line if you want to switch to non-root user
# USER appuser

EXPOSE 8080

CMD ["python", "app.py"]
