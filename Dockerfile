FROM python:alpine

WORKDIR /app

COPY main.py /app
COPY domains.json /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["python", "main.py"]
