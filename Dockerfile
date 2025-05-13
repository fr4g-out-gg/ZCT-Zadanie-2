FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install psycopg2-binary

EXPOSE 5000

CMD ["python", "app.py"]
