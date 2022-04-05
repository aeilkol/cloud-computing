# cloud-computig

How to get database running and ingest data:

1. Create `.env`-file in folder `database` according to `example.env`.
2. In `database` run `docker-compose up` to start database.
3. In `database/ingest` run `ingest.py` to create tables and ingest all data but the flight data.


How to run actual code:

1. In every microservice folder run `sh build_protobufs.sh`
2. Create `.env`-file in every microservice folder according to `example.env`
3. Install all the requirements to your python environment with `python3 -m pip install -r requirements.txt` in every microservice/outbound folder.
4. Copy file `runtime_interceptor.py` to `data_analysis` and `data_delivery` folders.

How to then run the containers:
1. In `src` folder run all the docker build commands commented into the `docker_run_{script name}.sh` files.
2. Run all the `docker_run_{script name}.sh` scripts.