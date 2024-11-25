FROM python:3.10.11-alpine3.18

RUN apk add --no-cache gcc musl-dev libffi-dev python3-dev openssl-dev

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py", "-a", "1"]
