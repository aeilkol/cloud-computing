import time
import os
import argparse
import sys
from concurrent import futures

import dotenv
import psycopg2, psycopg2.extras
import grpc

from grpc_interceptor import ExceptionToStatusInterceptor
import shapely, shapely.wkb

from data_delivery_pb2 import (
    Airport,
    AirportResponse,
    Location,
    AirportType,

    Flight,
    FlightResponse,

    CovidCase,
    CovidCaseResponse,

    AirportCovidCase,
    AirportCovidCaseResponse,

    FlightByDate,
    FlightsByDateResponse
)
import data_delivery_pb2_grpc

from logging_pb2_grpc import LoggingServiceStub
from redirect_output import LoggingRedirector

from runtime_interceptor import RuntimeInterceptor

class DataDeliveryService(data_delivery_pb2_grpc.DataDeliveryServicer):

    def __init__(self, connection):
        self.database_service = DataDeliveryDatabaseService(connection)

    def Airports(self, request, context):
        airport_type = AirportType.Name(request.airport_type)
        airports = self.database_service.get_airports(request.continent, airport_type)
        airport_objects = []
        for airport in airports:
            shapely_location = shapely.wkb.loads(airport['location'], hex=True)
            airport_objects.append(
                Airport(
                    name=airport['name'],
                    code=airport['code'],
                    location=Location(latitude=shapely_location.y, longitude=shapely_location.x),
                    type=airport['type']
                )
            )
        return AirportResponse(airports=airport_objects)

    def Flights(self, request, context):
        connections = self.database_service.get_flights(request.date, request.continent)
        connection_objects = [Flight(src=connection['origin'],
                                     dest=connection['destination'],
                                     cardinality=connection['cardinality'])
                              for connection in connections]
        return FlightResponse(flights=connection_objects)

    def CovidCases(self, request, context):
        covid_cases = self.database_service.get_covid_cases(request.date, request.area_level)
        covid_case_objects = [CovidCase(region=covid_case['region_id'],
                                        date=str(covid_case['date']),
                                        incidence=covid_case['incidence'])
                              for covid_case in covid_cases]
        return CovidCaseResponse(covid_cases=covid_case_objects)

    def AirportCovidCases(self, request, context):
        airport_covid_cases = self.database_service.get_airport_covid_cases(request.airport_code)
        airport_covid_case_objects = [AirportCovidCase(date=str(incidence['date']),
                                                       incidence=incidence['incidence'])
                                      for incidence in airport_covid_cases['incidences']]
        return AirportCovidCaseResponse(incidences=airport_covid_case_objects,
                                        airport_code=request.airport_code,
                                        region=airport_covid_cases['region_id'])

    def FlightsByDate(self, request, context):
        flights_by_date = self.database_service.get_flights_by_date(request.airport_code, request.origin)
        flights_by_date_objects = [FlightByDate(date=str(flight_by_date['date']),
                                                count=flight_by_date['count'])
                                   for flight_by_date in flights_by_date]
        return FlightsByDateResponse(flights=flights_by_date_objects)


class DataDeliveryDatabaseService():

    def __init__(self, connection):
        self.connection = connection

    def get_airports(self, continent=None, airport_type=None):
        sql = '''
            SELECT * FROM airports
            WHERE (continent = %(continent)s OR %(continent)s IS NULL)
              AND ("type" = %(airport_type)s OR %(airport_type)s IS NULL)
            '''
        params = {
            'continent': continent,
            'airport_type': airport_type
        }
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()

    def get_flights(self, date, continent=None):
        sql = '''
        SELECT f.origin, f.destination, COUNT(*) AS cardinality FROM flights AS f
        JOIN airports AS a_o
          ON a_o.code = f.origin
        JOIN airports AS a_d
          ON a_d.code = f.destination
        WHERE (firstseen::date=TO_DATE(%(date)s, 'YYYY-MM-DD') OR lastseen::date=TO_DATE(%(date)s, 'YYYY-MM-DD'))
          AND (a_o.continent=%(continent)s AND a_d.continent=%(continent)s OR %(continent)s IS NULL)
        GROUP BY f.origin, f.destination
        '''
        params = {
            'date': date,
            'continent': continent
        }
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()

    def get_covid_cases(self, date, area_level=None):
        sql = '''
        SELECT * FROM covid_cases 
        WHERE date=TO_DATE(%s, 'YYYY-MM-DD')
        '''
        params =[date]
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()

    def get_airport_covid_cases(self, airport_code, area_level=3):
        region_id = self.get_airport_region(airport_code, area_level)
        sql = '''
        SELECT c_c.incidence, c_c.date FROM covid_cases c_c
        JOIN regions r
        ON c_c.region_id = r.id AND r.id = %(region_id)s
        '''
        params = {
            'region_id': region_id
        }
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        return {
            'region_id': region_id,
            'incidences': cursor.fetchall()
        }

    def get_airport_region(self, airport_code, area_level):
        sql = '''
        SELECT r.id AS region_id FROM regions r
        LEFT JOIN airports a
        ON ST_INTERSECTS(a.location, r.geom)
        WHERE a.code = %(airport_code)s
        AND r.level = %(area_level)s
        '''
        params = {
            'airport_code': airport_code,
            'area_level': area_level
        }
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        region_return = cursor.fetchone()
        if len(region_return) == 0:
            raise LookupError('No region for this airport could be found')
        return region_return['region_id']

    def get_flights_by_date(self, airport_code, origin):
        column = 'origin' if origin else 'destination'
        sql = '''
        SELECT firstseen::DATE AS date, COUNT(*) AS count FROM flights
        WHERE {} = %(airport_code)s
        GROUP BY firstseen::DATE
        ORDER BY firstseen::DATE
        '''.format(column, column)
        params = {
            'airport_code': airport_code
        }
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        return cursor.fetchall()


def serve(logging_address):

    logging_channel = grpc.insecure_channel(logging_address, options=(('grpc.enable_http_proxy', 0),))
    logging_client = LoggingServiceStub(logging_channel)

    stdout_redirector = LoggingRedirector(logging_client, 'data_delivery', True)
    stderr_redirector = LoggingRedirector(logging_client, 'data_delivery', False)

    retries = 0
    max_retries = 5
    connected = False
    while retries < max_retries and not connected:
        try:
            stdout_redirector.write('Service started.')
            sys.stdout = stdout_redirector
            sys.stderr = stderr_redirector
            connected = True
        except Exception as e:
            retries += 1
            time.sleep(5)
            print(e)
    if not connected:
        print('Logging service not available, will use console instead.')
    else:
        print('Logging service connected.')

    retries = 0
    max_retries = 5
    connected = False
    while retries < max_retries and not connected:
        try:
            conn = psycopg2.connect(user=os.environ['DB_USER'], password=os.environ['DB_PASS'],
                                    host=os.environ['DB_HOST'],
                                    port=os.environ['DB_PORT'], dbname=os.environ['DB_NAME'])
            connected = True
            print('Connected to database.')
        except psycopg2.OperationalError:
            retries += 1
            time.sleep(5)
            if retries == max_retries:
                raise EnvironmentError('Database connection failed')

    interceptors = [ExceptionToStatusInterceptor(), RuntimeInterceptor(conn)]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    data_delivery_pb2_grpc.add_DataDeliveryServicer_to_server(
        DataDeliveryService(conn), server
    )

    server.add_insecure_port("[::]:{}".format(os.environ['OUT_PORT']))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--env', '-e')
    arguments = argparser.parse_args()
    env_path = arguments.env if arguments.env else '.env'
    dotenv.load_dotenv(arguments.env)

    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        logging_host = os.environ['LOGGING_ENDPOINT_SERVICE_HOST']
        logging_port = os.environ['LOGGING_ENDPOINT_SERVICE_PORT']
    else:
        dotenv.load_dotenv(arguments.env)
        logging_host = os.environ['LOGGING_ADDRESS']
        logging_port = os.environ['LOGGING_PORT']
    logging_address = '{}:{}'.format(logging_host, logging_port)

    serve(logging_address)