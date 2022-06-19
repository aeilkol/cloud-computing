FROM python:3.8
RUN ["mkdir", "/home/logging"]
WORKDIR /home/logging

COPY microservices/logging microservices/logging
COPY protobufs/ protobufs/
WORKDIR microservices/logging
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../../protobufs

CMD ["python3", "logging_service.py"]
