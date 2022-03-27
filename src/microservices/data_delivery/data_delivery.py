import time
import os
from concurrent import futures

import dotenv
import psycopg2
import grpc
from grpc_interceptor import ExceptionToStatusInterceptor

from data_delivery_pb2 import (
    Airport,
    AirportResponse,
    CovidCasesResponse,
    CovidCase
    
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
            
    def CovidCases(self, request, context):
        covidCases = self.database_service.getCovidCases(request.date, request.area_level)
        covidCases_objects = []
        for CovidCase in covidCases:
            covidCases_objects.append(
                CovidCase(
                    contry = CovidCase['contry'],
                    week = CovidCase['week'],
                    covidCases = CovidCase['covidCases']
                )
            )
        return CovidCasesResponse(covidCases=covidCases_objects)
       


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

    def getCovidCases(self, date, area_level=None):
        sql = 'SELECT * FROM covid_cases WHERE year_week=%s'
        params =[]
        params.append(getDateInWeekFormat(date))
        cursor = self.connection.cursor()
        cursor.query(sql, params)
        return cursor.fetchall()
    
    def getDateInWeekFormat(self, date):
        return date

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
