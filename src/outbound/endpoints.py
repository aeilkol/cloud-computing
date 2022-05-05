import os

import grpc
import dotenv

from data_delivery_pb2 import AirportRequest, CovidCaseRequest, FlightRequest, AirportCovidCaseRequest
from data_delivery_pb2_grpc import DataDeliveryStub
from data_analysis_pb2 import AirportAnalysisRequest
from data_analysis_pb2_grpc import DataAnalysisStub
from administrator_analysis_pb2 import RequestAnalysisRequest
from administrator_analysis_pb2_grpc import AdministratorAnalysisStub

from google.protobuf.json_format import MessageToDict

if os.environ.get('https_proxy'):
    del os.environ['https_proxy']
if os.environ.get('http_proxy'):
    del os.environ['http_proxy']

dotenv.load_dotenv('.env')

data_delivery_host = os.environ['DATA_DELIVERY_ADDRESS'] if 'DATA_DELIVERY_ADDRESS' in os.environ else os.environ[
    'DATA_DELIVERY_ENDPOINT_SERVICE_HOST']
data_delivery_port = os.environ['DATA_DELIVERY_PORT'] if 'DATA_DELIVERY_PORT' in os.environ else os.environ[
    'DATA_DELIVERY_ENDPOINT_SERVICE_PORT']
data_delivery_address = '{}:{}'.format(data_delivery_host, data_delivery_port)
data_delivery_channel = grpc.insecure_channel(data_delivery_address, options=(('grpc.enable_http_proxy', 0),))
data_delivery_client = DataDeliveryStub(data_delivery_channel)

data_analysis_host = os.environ['DATA_ANALYSIS_ADDRESS'] if 'DATA_ANALYSIS_ADDRESS' in os.environ else os.environ[
    'DATA_ANALYSIS_ENDPOINT_SERVICE_HOST']
data_analysis_port = os.environ['DATA_ANALYSIS_PORT'] if 'DATA_ANALYSIS_PORT' in os.environ else os.environ[
    'DATA_ANALYSIS_ENDPOINT_SERVICE_PORT']
data_analysis_address = '{}:{}'.format(data_analysis_host, data_analysis_port)
data_analysis_channel = grpc.insecure_channel(data_analysis_address, options=(('grpc.enable_http_proxy', 0),))
data_analysis_client = DataAnalysisStub(data_analysis_channel)

administrator_analysis_host = os.environ['ADMINISTRATOR_ANALYSIS_ADDRESS'] if 'ADMINISTRATOR_ANALYSIS_ADDRESS' in os.environ else os.environ[
    'ADMINISTRATOR_ANALYSIS_ENDPOINT_SERVICE_HOST']
administrator_analysis_port = os.environ['ADMINISTRATOR_ANALYSIS_PORT'] if 'ADMINISTRATOR_ANALYSIS_PORT' in os.environ else os.environ[
    'ADMINISTRATOR_ANALYSIS_ENDPOINT_SERVICE_PORT']
administrator_analysis_address = '{}:{}'.format(administrator_analysis_host, administrator_analysis_port)
administrator_analysis_channel = grpc.insecure_channel(administrator_analysis_address, options=(('grpc.enable_http_proxy', 0),))
administrator_analysis_client = AdministratorAnalysisStub(administrator_analysis_channel)

if 'DATA_DELIVERY_ADDRESS' in os.environ:
    print(os.environ['DATA_DELIVERY_ADDRESS'])
print('Adresses: (Data Delivery {}, Data Analysis {}, Admin Analysis {}'.format(data_delivery_address, data_analysis_address, administrator_analysis_address))

def read_all_airports(continent, airport_type=1):
    request = AirportRequest(
        continent=continent,
        airport_type=airport_type
    )
    response = data_delivery_client.Airports(request)
    return MessageToDict(response)


def read_all_flights(date, continent):
    request = FlightRequest(
        date=date,
        continent=continent
    )
    response = data_delivery_client.Flights(request)
    return MessageToDict(response)


def read_all_covid_cases(date, area_level):
    request = CovidCaseRequest(
        date=date,
        area_level=area_level
    )
    response = data_delivery_client.CovidCases(request)
    return MessageToDict(response)


def read_airport_covid_cases(airport_code):
    request = AirportCovidCaseRequest(airport_code=airport_code)
    response = data_delivery_client.AirportCovidCases(request)
    return MessageToDict(response)


def read_statistics(airport_code, origin):
    request = AirportAnalysisRequest(airport_code=airport_code, origin=origin)
    response = data_analysis_client.AirportAnalysis(request)
    return MessageToDict(response)

def read_runtimes(service, request_type, start_time=None, end_time=None):
    request = RequestAnalysisRequest(service=service, request=request_type, start_time=start_time, end_time=end_time)
    response = administrator_analysis_client.RequestAnalysis(request)
    return MessageToDict(response)
