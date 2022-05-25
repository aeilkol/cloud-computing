# cloud-computig

How to get database running and ingest data:

1. Create `.env`-file in folder `database` according to `example.env`.
2. In `database` run `docker-compose up` to start database.
3. In `database/ingest` run `ingest.py` to create tables and ingest all data.


How to run actual code:

1. In `src` folder, run `sh scripts/build_all_protobufs.sh`
2. In `src` folder, run `sh scripts/copy_redirect_output.sh`
3. Create `.env`-file in every microservice and the outbound folder according to `example.env`
4. Install all the requirements to your python environment with `python3 -m pip install -r requirements.txt` in every microservice/outbound folder.
5. Copy file `runtime_interceptor.py` to `data_analysis` and `data_delivery` folders.
6. Run all service files in the microservices folder.

How to then run the containers:
1. In `src` folder, run `sh scripts/setup.sh`.
2. Run all the `docker_run_{script name}.sh` scripts.