FROM python:3
RUN ["mkdir", "/home/ingest"]
WORKDIR /home/ingest

COPY . .
RUN pip3 install -r requirements.txt

CMD ["python3", "ingest.py"]