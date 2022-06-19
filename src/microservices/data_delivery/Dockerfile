FROM python:3.8
WORKDIR /home/data_delivery

COPY microservices/data_delivery microservices/data_delivery
COPY protobufs protobufs
COPY runtime_interceptor/runtime_interceptor.py microservices/data_delivery/runtime_interceptor.py
WORKDIR microservices/data_delivery
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../../protobufs

CMD ["python3", "data_delivery.py"]