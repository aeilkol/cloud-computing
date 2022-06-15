import datetime
import argparse
from concurrent import futures
import sys
import os
import time

import dotenv
import grpc
from google.protobuf.json_format import MessageToDict
import psycopg2

from grpc_interceptor import ExceptionToStatusInterceptor
import data_analysis_pb2_grpc
from data_analysis_pb2 import (
    AirportAnalysis,
    AirportAnalysisResponse
)
from data_delivery_pb2_grpc import DataDeliveryStub
from data_delivery_pb2 import (
    AirportCovidCaseRequest,
    FlightsByDateRequest
)

from logging_pb2_grpc import LoggingServiceStub
from redirect_output import LoggingRedirector

from runtime_interceptor import RuntimeInterceptor


class DataAnalysisService(data_analysis_pb2_grpc.DataAnalysisServicer):

    def __init__(self):
        data_delivery_host = os.environ['DATA_DELIVERY_ADDRESS'] if 'DATA_DELIVERY_ADDRESS' in os.environ else os.environ['DATA_DELIVERY_ENDPOINT_SERVICE_HOST']
        data_delivery_port = os.environ['DATA_DELIVERY_PORT'] if 'DATA_DELIVERY_PORT' in os.environ else os.environ['DATA_DELIVERY_ENDPOINT_SERVICE_PORT']
        data_delivery_address = '{}:{}'.format(data_delivery_host, data_delivery_port)
        data_delivery_channel = grpc.insecure_channel(data_delivery_address, options=(('grpc.enable_http_proxy', 0),))
        self.data_delivery_client = DataDeliveryStub(data_delivery_channel)


    def AirportAnalysis(self, request, context):

        flights_request = FlightsByDateRequest(
            airport_code=request.airport_code,
            origin=request.origin
        )
        flights_response = self.data_delivery_client.FlightsByDate(flights_request)
        covid_case_request = AirportCovidCaseRequest(
            airport_code=request.airport_code,
            area_level=3
        )
        covid_case_response = self.data_delivery_client.AirportCovidCases(covid_case_request)
        flight_dict = {}
        for flight in flights_response.flights:
            flight_dict[flight.date] = flight.count
        incidences = [incidence_dict['incidence'] for incidence_dict in MessageToDict(covid_case_response)['incidences']
                      if 'incidence' in incidence_dict]
        max_incidence = max(incidences)
        airport_analysis_objects = []
        for incidence in covid_case_response.incidences:
            covid_date = datetime.datetime.strptime(incidence.date, '%Y-%m-%d').date()
            year_before = self.__subtract_years(covid_date, 1)
            year_before_str = year_before.strftime('%Y-%m-%d')
            if year_before_str not in flight_dict or incidence.date not in flight_dict:
                continue
            flights_year_before = flight_dict[year_before_str]
            flights_year_current = flight_dict[incidence.date]
            relative_incidence = incidence.incidence / max_incidence
            if relative_incidence > 0 and flights_year_before > 0:
                covid_flight_factor = (flights_year_current / flights_year_before) * relative_incidence
                airport_analysis_objects.append(AirportAnalysis(date=incidence.date,
                                                                covid_flight_factor=covid_flight_factor))
        return AirportAnalysisResponse(analysis=airport_analysis_objects)

    @staticmethod
    def __subtract_years(dt, years):
        try:
            dt = dt.replace(year=dt.year - years)
        except ValueError:
            dt = dt.replace(year=dt.year - years, day=dt.day - 1)
        return dt

def serve():

    logging_host = os.environ['LOGGING_ADDRESS'] if 'LOGGING_ADDRESS' in os.environ else os.environ[
        'LOGGING_ENDPOINT_SERVICE_HOST']
    logging_port = os.environ['LOGGING_PORT'] if 'LOGGING_PORT' in os.environ else os.environ[
        'LOGGING_ENDPOINT_SERVICE_PORT']
    logging_address = '{}:{}'.format(logging_host, logging_port)
    logging_channel = grpc.insecure_channel(logging_address, options=(('grpc.enable_http_proxy', 0),))
    logging_client = LoggingServiceStub(logging_channel)

    stdout_redirector = LoggingRedirector(logging_client, 'data_analysis', True)
    stderr_redirector = LoggingRedirector(logging_client, 'data_analysis', False)

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
        except psycopg2.OperationalError:
            retries += 1
            time.sleep(5)
            if retries == max_retries:
                raise EnvironmentError('Database connection failed')

    interceptors = [ExceptionToStatusInterceptor(), RuntimeInterceptor(conn)]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    data_analysis_pb2_grpc.add_DataAnalysisServicer_to_server(
        DataAnalysisService(), server
    )

    server.add_insecure_port("[::]:{}".format(os.environ['OUT_PORT']))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    if not 'DATA_DELIVERY_ADDRESS' in os.environ:
        argparser = argparse.ArgumentParser()
        argparser.add_argument('--env', '-e')
        arguments = argparser.parse_args()
        env_path = arguments.env if arguments.env else '.env'
        dotenv.load_dotenv(arguments.env)
    serve()
