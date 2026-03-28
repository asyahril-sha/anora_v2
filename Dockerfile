FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ make curl sqlite3 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 mylove && chown -R mylove:mylove /app
USER mylove

CMD ["python", "main.py"]
