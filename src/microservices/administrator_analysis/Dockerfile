FROM python:3.8
WORKDIR /home/administrator_analysis

COPY microservices/administrator_analysis microservices/administrator_analysis
COPY protobufs protobufs
WORKDIR microservices/administrator_analysis
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../../protobufs

CMD ["python3", "administrator_analysis.py"]