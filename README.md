# cloud-computig

How to get database running and ingest data:

1. Create `.env`-file in folder `database` according to `example.env`.
2. In `database/ingest` run `sudo docker build . -f Dockerfile -t ingest` to build the ingest-container.
3. In `database` run `docker-compose up` to start database.
4. In `databae/ingest` run `ingest.py` to create tables and ingest all data but the flight data.
5. Download all csv files from `https://zenodo.org/record/6325961#collapseTwo` in the years 2020 and 2021.
6. Unzip all csv files and put them into an appropriate folder.
7. Start psql in terminal with `psql -U postgres -p 5432 -h localhost flights_covid`.
8. In psql run `\copy imported_flights(callsign, number, icao24, registration, typecode, origin, destination, firstseen, lastseen, day, latitude_1, longitude_1, altitude_1, latitude_2, longitude_2, altitude_2) from '<path_to_csv>' with (format csv, header);` for every existing csv file.

How to run actual code:

1. In `src` folder run `python -m grpc_tools.protoc -I src/protobufs --python_out=src/microservices/data_delivery --grpc_python_out=src/microservices/data_delivery src/protobufs/data_delivery.proto`.
2. In `src` folder run `python -m grpc_tools.protoc -I src/protobufs --python_out=src/outbound --grpc_python_out=src/outbound src/protobufs/data_delivery.proto`.
3. Create `.env`-file in folder data_delivery according to `example.env`
4. Run `src/microservices/data_delivery.py` and `src/oubound/outbound.py`