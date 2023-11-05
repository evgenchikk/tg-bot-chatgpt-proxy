FROM python:3.10-slim-buster

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY sql /sql
COPY src .

CMD [ "python", "main.py" ]
