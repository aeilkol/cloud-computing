import csv
import json
import os
import os.path
import time
import zipfile
from urllib import request
import requests

import dotenv
import psycopg2
import psycopg2.errors
from shapely.geometry import shape


def check_if_db_contains_data(cursor):
    pass


def check_airport_table(cursor):
    sql = 'SELECT COUNT(*) AS count FROM airports'

    cursor.execute(sql, [])
    count = cursor.fetchone()


def download_datasets():

    path = 'datasets'

    if not os.path.exists(path):
        os.mkdir(path)

    flights_path = download_flight_data(path)
    print('Downloaded flight data to {}'.format(flights_path))

    covid_path = download_covid_data(path)
    print('Downloaded covid case data to {}'.format(covid_path))

    regions_path = download_regions_data(path)
    print('Downloaded regions data to {}'.format(regions_path))

    airport_path = download_airport_data(path)
    print('Downloaded airport data to {}'.format(airport_path))

    return {
        'airports': airport_path,
        'regions': regions_path,
        'covid': covid_path,
        'flights': flights_path
    }


def download_flight_data(path):

    return 'datasets/flights' # has to be predownloaded because zenodo api does not support file sizes larger than 100 MB


def download_regions_data(path):

    regions_filename = 'regions.geojson'
    regions_path = os.path.join(path, regions_filename)

    if not os.path.exists(regions_path):
        regions_url = 'https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2016_4326.geojson'
        request.urlretrieve(regions_url, regions_path)

    return regions_path


def download_covid_data(path):

    covid_filename = 'covid_cases.csv'
    covid_path = os.path.join(path, covid_filename)

    if not os.path.exists(covid_path):
        covid_url = 'https://opendata.ecdc.europa.eu/covid19/subnationalcasedaily/csv/data.csv'
        request.urlretrieve(covid_url, covid_path)

    return covid_path


def download_airport_data(path):

    airport_filename = 'airports.csv'
    airport_path = os.path.join(path, airport_filename)

    if not os.path.exists(airport_path):
        covid_url = 'http://ourairports.com/data/airports.csv'
        request.urlretrieve(covid_url, airport_path)

    return airport_path


def create_tables(cursor):

    create_db_sql = ''' 
    DROP TABLE IF EXISTS airports CASCADE;
    CREATE TABLE airports (
        code VARCHAR(25) PRIMARY KEY,
        name VARCHAR(128),
        type VARCHAR(32),
        elevation REAL,
        continent VARCHAR(2),
        location GEOGRAPHY(POINT)
    );             
    DROP TABLE IF EXISTS flights CASCADE;
    CREATE TABLE flights (
        id SERIAL PRIMARY KEY,
        callsign VARCHAR(8),
        typecode VARCHAR(25),
        origin VARCHAR(25) REFERENCES airports(code),
        destination VARCHAR(25) REFERENCES airports(code),
        firstseen TIMESTAMP,
        lastseen TIMESTAMP
    );
                
    DROP TABLE IF EXISTS imported_flights CASCADE;
    CREATE TABLE imported_flights (
        id SERIAL PRIMARY KEY,
        callsign VARCHAR(8),
        number VARCHAR(10),
        icao24 VARCHAR(10),
        registration VARCHAR(30),
        typecode VARCHAR(50),
        origin VARCHAR(25),
        destination VARCHAR(25),
        firstseen TIMESTAMP,
        lastseen TIMESTAMP,
        "day" VARCHAR(50),
        latitude_1 FLOAT,
        longitude_1 FLOAT,
        altitude_1 FLOAT,
        latitude_2 FLOAT,
        longitude_2 FLOAT,
        altitude_2 FLOAT
    );
    DROP TABLE IF EXISTS regions CASCADE;
    CREATE TABLE regions (
        id VARCHAR(5) PRIMARY KEY,
        level SMALLINT,
        geom GEOGRAPHY(MULTIPOLYGON),
        center_code VARCHAR(2),
        name VARCHAR(128),
        mount_type SMALLINT,
        urbn_type SMALLINT,
        coast_type SMALLINT
    );
    DROP TABLE IF EXISTS covid_cases CASCADE;
    CREATE TABLE covid_cases (
        id SERIAL PRIMARY KEY,
        region_id VARCHAR(5) REFERENCES regions(id),
        date DATE,
        incidence REAL
    );
    '''
    #cursor.execute(create_db_sql, [])


def ingest(cursor, destinations):
    ingest_airports(cursor, destinations['airports'])
    print('Ingested airports')
    ingest_regions(cursor, destinations['regions'])
    print('Ingested regions')
    ingest_covid(cursor, destinations['covid'])
    print('Ingested covid cases')
    ingest_flights(cursor, destinations['flights'])
    print('Ingested flights')


def ingest_airports(cursor, path):

    sql = '''
    INSERT INTO airports (code, name, type, elevation, continent, location) VALUES
    (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326));
    '''

    with open(path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for line in csvreader:
            insert = [line['ident'], line['name'], line['type'], None, line['continent'], line['longitude_deg'], line['latitude_deg']]
            insert[3] = line['elevation_ft'] if line['elevation_ft'] else None
            #cursor.execute(sql, insert)


def ingest_regions(cursor, path):

    sql = '''
    INSERT INTO regions (id, level, geom, center_code, name, mount_type, urbn_type, coast_type) VALUES 
    (%s, %s, ST_Multi(ST_SetSRID(%s::geometry, 4326)), %s, %s, %s, %s, %s)
    '''

    with open(path, 'r') as geojsonfile:
        json_object = json.load(geojsonfile)
        for region in json_object['features']:
            geometry = shape(region['geometry'])
            insert = (region['properties']['NUTS_ID'], region['properties']['LEVL_CODE'], geometry.wkb_hex,
                      region['properties']['CNTR_CODE'], region['properties']['NAME_LATN'],
                      region['properties']['MOUNT_TYPE'], region['properties']['URBN_TYPE'],
                      region['properties']['COAST_TYPE'])
            cursor.execute(sql, insert)


def ingest_covid(cursor, path):
    sql = '''
        INSERT INTO covid_cases (region_id, incidence, date) VALUES
        (%s, %s, TO_DATE(%s, 'YYYYMMDD'));
        '''

    with open(path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for line in csvreader:
            insert = [line['nuts_code'], None, line['date']]
            insert[1] = line['rate_14_day_per_100k'] if line['rate_14_day_per_100k'] else None
            cursor.execute(sql, insert)


def ingest_flights(cursor, path):
    pass
    # sql = '''
    #         INSERT INTO flights (callsign, typecode, origin, destination, firstseen, lastseen) VALUES
    #         (%s, %s, %s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS+00:00'),
    #         TO_TIMESTAMP(%s, 'YYYY-MM-DD HH24:MI:SS+00:00'));
    #         '''
    #
    # foreign_key_exists_sql = '''
    #     SELECT count(*) AS c FROM airports WHERE code=%s;
    # '''
    # filenames = os.listdir(path)
    # max_flights = 1000000000
    # flights = 0
    # start = time.time()
    # for filename in filenames:
        # with open(os.path.join(path, filename), 'r') as csvfile:
        #     csvreader = csv.DictReader(csvfile)
        #     for line in csvreader:
        #         if line['origin'] and line['destination']:
        #             insert = [line['callsign'], line['typecode'], line['origin'], line['destination'],
        #                       line['firstseen'], line['lastseen']]
        #             cursor.execute(foreign_key_exists_sql, [line['origin']])
        #             origin_exists = cursor.fetchone()[0]
        #             cursor.execute(foreign_key_exists_sql, [line['destination']])
        #             destination_exists = cursor.fetchone()[0]
        #             if origin_exists and destination_exists:
        #                 cursor.execute(sql, insert)
        #         flights += 1
        #         if flights >= max_flights:
        #             return
        #         if flights % 100000 == 0:
        #             print('Flights ingested: {}, Time: {}'.format(flights, time.time() - start))
        # sql = '''
        # COPY imported_flights
        # FROM {}
        # WITH (format csv, header)
        # '''.format(os.path.join(path, filename))
        # cursor.execute(sql)
        # print('Finished file {}'.format(filename))


if __name__ == '__main__':

    dotenv.load_dotenv('../.env')
    retries = 0
    max_retries = 5
    connected = False
    while retries < max_retries and not connected:
        try:
            conn = psycopg2.connect(user=os.environ['DB_USER'], password=os.environ['DB_PASS'], host=os.environ['DB_HOST'],
                                    port=os.environ['DB_PORT'], dbname=os.environ['DB_NAME'])
            connected = True
        except psycopg2.OperationalError:
            retries += 1
            time.sleep(5)
            if retries == max_retries:
                raise EnvironmentError('Database connection failed')


    cursor = conn.cursor()

    create_tables(cursor)
    conn.commit()

    paths = download_datasets()

    ingest(cursor, paths)

    conn.commit()
    conn.close()
