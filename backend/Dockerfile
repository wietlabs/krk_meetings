FROM amancevice/pandas:1.1.5
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
EXPOSE 5000
COPY . .
RUN pip install -e . --no-cache-dir
CMD python krk_meetings/run.py
