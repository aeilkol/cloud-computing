FROM python:3.8
WORKDIR /home/outbound

COPY outbound outbound
COPY protobufs protobufs
COPY openapi openapi
WORKDIR outbound
RUN pip3 install -r requirements.txt
RUN sh build_protobufs.sh ../protobufs

CMD ["python3", "outbound.py"]