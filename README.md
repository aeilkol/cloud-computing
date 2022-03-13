# cloud-computig

How to get database running and ingest data:

1. Create `.env`-file in folder `database` according to `example.env`.
2. In `database/ingest` run `sudo docker build . -f Dockerfile -t ingest` to build the ingest-container.
3. In `database` run `docker-compose up` to start database and ingestion.
