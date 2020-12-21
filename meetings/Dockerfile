FROM python:3.8-alpine
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
EXPOSE 8000
COPY . .
CMD gunicorn -w 4 -b 0.0.0.0:8000 app:app
