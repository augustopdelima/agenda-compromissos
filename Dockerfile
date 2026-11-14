FROM python:3.15.2-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["flask","--app","app:iniciar_app", "run", "--host=0.0.0.0", "--debug"]
