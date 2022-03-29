# cloud-computig

How to get database running and ingest data:

1. Create `.env`-file in folder `database` according to `example.env`.
2. In `database/ingest` run `sudo docker build . -f Dockerfile -t ingest` to build the ingest-container.
3. In `database` run `docker-compose up` to start database.
4. Run `database/ingest/ingest.py` to ingest data.
5. In `src` folder run `python -m grpc_tools.protoc -I src/protobufs --python_out=src/outbound --grpc_python_out=src/outbound src/protobufs/data_delivery.proto`.
6. Create `.env`-file in folder data_delivery according to `example.env`
7. Run `src/microservices/data_delivery.py` and `src/oubound/outbound.py`