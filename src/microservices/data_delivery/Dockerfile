FROM python:3
RUN ["mkdir", "/home/data_delivery"]
WORKDIR /home/delivery

COPY microservices/data_delivery microservices/data_delivery
COPY protobufs/ protobufs/
WORKDIR microservices/data_delivery
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../../protobufs

CMD ["python3", "data_delivery.py"]