FROM python:3
RUN ["mkdir", "/home/data_analysis"]
WORKDIR /home/analysis

COPY microservices/data_analysis microservices/data_analysis
COPY protobufs/ protobufs/
WORKDIR microservices/data_analysis
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../../protobufs

CMD ["python3", "data_analysis.py"]