import time
import os
from concurrent import futures

import dotenv
import psycopg2
import grpc
from grpc_interceptor import ExceptionToStatusInterceptor

from data_delivery_pb2 import (
    Airport,
    Flight,
    AirportResponse,
    FlightResponse,
    AirportCovidCase,
    AirportCovidCaseResponse
)
import data_delivery_pb2_grpc


class DataDeliveryService(data_delivery_pb2_grpc.DataDeliveryServicer):

    def __init__(self, connection):
        self.database_service = DataDeliveryDatabaseService(connection)

    def Airports(self, request, context):
        airports = self.database_service.getAirports(request.continent)
        airport_objects = []
        for airport in airports:
            airport_objects.append(
                Airport(
                    name=airport['name'],
                    code=airport['code']
                )
            )
        return AirportResponse(airports=airport_objects)

    def Flights(self, request, context):
        flights = self.database_service.getFlights(request.date, request.continent)
        flights_objects = []
        for flight in flights:
            flights_objects.append(
                Flight(
                    id=flight['id'],
                    src=flight['src'],
                    dest=flight['dest'],
                    firstseen=flight['flightseen'],
                    lastseen=flight['lastseen']
                )
            )
        return FlightResponse(flights=flights_objects)

    def AirportCovidCases(self, request, context):
        airportCovidCases = self.database_service.getAirportCovidCases(request.airport_code, request.area_level)
        cases_objects = []
        for case in airportCovidCases:
            cases_objects.append(
                AirportCovidCase(
                    region=case['region'],
                    incidence=case['incidence'],
                    date=case['date']
                )
            )
        return AirportCovidCaseResponse(covid_cases=cases_objects)

class DataDeliveryDatabaseService():

    def __init__(self, connection):
        self.connection = connection

    def getAirports(self, continent=None):
        sql = 'SELECT * FROM airports'
        params = []
        if continent:
            sql += ' WHERE continent=%s'
            params.append(continent)
        cursor = self.connection.cursor()
        cursor.query(sql, params)
        return cursor.fetchall()
    
    def getFlights(self, date, continent=None):
        #idk what if it is %s or %d
        sql = 'SELECT * FROM flights WHERE date=%s'
        params = [date]
        if continent:
            sql += ' AND continent=%s'
            params.append(continent)
        cursor = self.connection.cursor()
        cursor.query(sql, params)
        return cursor.fetchall()

    def getAirportCovidCases(self, airport_code, area_level):
        sql = 'SELECT * FROM covid_cases WHERE airport_code=%s AND area_level=%s'
        params = [airport_code, area_level]
        cursor = self.connection.cursor()
        cursor.query(sql, params)
        return cursor.fetchall()


def serve():

    retries = 0
    max_retries = 5
    connected = False
    while retries < max_retries and not connected:
        try:
            conn = psycopg2.connect(user=os.environ['DB_USER'], password=os.environ['DB_PASS'],
                                    host=os.environ['DB_HOST'],
                                    port=os.environ['DB_PORT'], dbname=os.environ['DB_NAME'])
            connected = True
        except psycopg2.OperationalError:
            retries += 1
            time.sleep(5)
            if retries == max_retries:
                raise EnvironmentError('Database connection failed')

    interceptors = [ExceptionToStatusInterceptor()]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    data_delivery_pb2_grpc.add_DataDeliveryServicer_to_server(
        DataDeliveryService(conn), server
    )

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':

    dotenv.load_dotenv('.env')
    serve()
