import os
import sys
import time

import grpc
import dotenv

from google.protobuf.json_format import MessageToDict

from data_delivery_pb2 import AirportRequest, CovidCaseRequest, FlightRequest, AirportCovidCaseRequest
from data_delivery_pb2_grpc import DataDeliveryStub
from data_analysis_pb2 import AirportAnalysisRequest
from data_analysis_pb2_grpc import DataAnalysisStub
from administrator_analysis_pb2 import RequestAnalysisRequest
from administrator_analysis_pb2_grpc import AdministratorAnalysisStub
from logging_pb2_grpc import LoggingServiceStub

from redirect_output import LoggingRedirector

if os.environ.get('https_proxy'):
    del os.environ['https_proxy']

dotenv.load_dotenv('.env')
if 'KUBERNETES_SERVICE_HOST' in os.environ:
    data_delivery_host = os.environ['DATA_DELIVERY_ENDPOINT_SERVICE_HOST']
    data_delivery_port = os.environ['DATA_DELIVERY_ENDPOINT_SERVICE_PORT']
    data_analysis_host = os.environ['DATA_ANALYSIS_ENDPOINT_SERVICE_HOST']
    data_analysis_port = os.environ['DATA_ANALYSIS_ENDPOINT_SERVICE_PORT']
    administrator_analysis_host = os.environ['ADMINISTRATOR_ANALYSIS_ENDPOINT_SERVICE_HOST']
    administrator_analysis_port = os.environ['ADMINISTRATOR_ANALYSIS_ENDPOINT_SERVICE_PORT']
    logging_host = os.environ['LOGGING_ENDPOINT_SERVICE_HOST']
    logging_port = os.environ['LOGGING_ENDPOINT_SERVICE_PORT']
else:
    data_delivery_host = os.environ['DATA_DELIVERY_ADDRESS']
    data_delivery_port = os.environ['DATA_DELIVERY_PORT']
    data_analysis_host = os.environ['DATA_ANALYSIS_ADDRESS']
    data_analysis_port = os.environ['DATA_ANALYSIS_PORT']
    administrator_analysis_host = os.environ['ADMINISTRATOR_ANALYSIS_ADDRESS']
    administrator_analysis_port = os.environ['ADMINISTRATOR_ANALYSIS_PORT']
    logging_host = os.environ['LOGGING_ADDRESS']
    logging_port = os.environ['LOGGING_PORT']

data_delivery_address = '{}:{}'.format(data_delivery_host, data_delivery_port)
data_delivery_channel = grpc.insecure_channel(data_delivery_address, options=(('grpc.enable_http_proxy', 0),))
data_delivery_client = DataDeliveryStub(data_delivery_channel)

data_analysis_address = '{}:{}'.format(data_analysis_host, data_analysis_port)
data_analysis_channel = grpc.insecure_channel(data_analysis_address, options=(('grpc.enable_http_proxy', 0),))
data_analysis_client = DataAnalysisStub(data_analysis_channel)

administrator_analysis_address = '{}:{}'.format(administrator_analysis_host, administrator_analysis_port)
administrator_analysis_channel = grpc.insecure_channel(administrator_analysis_address, options=(('grpc.enable_http_proxy', 0),))
administrator_analysis_client = AdministratorAnalysisStub(administrator_analysis_channel)

logging_address = '{}:{}'.format(logging_host, logging_port)
logging_channel = grpc.insecure_channel(logging_address, options=(('grpc.enable_http_proxy', 0),))
logging_client = LoggingServiceStub(logging_channel)

stdout_redirector = LoggingRedirector(logging_client, 'outbound', True)
stderr_redirector = LoggingRedirector(logging_client, 'outbound', False)

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

print('Running in Kubernetes: {}'.format('KUBERNETES_SERVICE_HOST' in os.environ))
print('Adresses: (Data Delivery {}, Data Analysis {}, Admin Analysis {}, Logging {})'
      .format(data_delivery_address, data_analysis_address, administrator_analysis_address, logging_address))

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

def health_check():
    return 'Healthy'