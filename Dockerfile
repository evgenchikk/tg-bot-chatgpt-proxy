FROM python:3.10-alpine

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

COPY sql /sql
COPY src .

CMD [ "python", "main.py" ]
