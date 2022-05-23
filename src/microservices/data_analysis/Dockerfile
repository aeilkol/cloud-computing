FROM python:3.9
WORKDIR /home/data_analysis

COPY microservices/data_analysis microservices/data_analysis
COPY protobufs/ protobufs/
COPY runtime_interceptor/runtime_interceptor.py microservices/data_delivery/runtime_interceptor.py
WORKDIR microservices/data_analysis
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../../protobufs

CMD ["python3", "data_analysis.py"]