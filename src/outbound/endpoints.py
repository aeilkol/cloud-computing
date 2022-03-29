import grpc

from data_delivery_pb2 import AirportRequest, CovidCaseRequest
from data_delivery_pb2_grpc import DataDeliveryStub
from google.protobuf.json_format import MessageToDict

data_delivery_channel = grpc.insecure_channel('localhost:50051')
data_delivery_client = DataDeliveryStub(data_delivery_channel)

def read_all_airports(continent, airport_type):
    request = AirportRequest(
        continent=continent
    )
    response = data_delivery_client.Airports(request)
    return response

def read_all_flights():
    pass

def read_all_covid_cases(date, area_level):
    request = CovidCaseRequest(
        date=date,
        area_level=area_level
    )
    response = data_delivery_client.CovidCases(request)
    return MessageToDict(response)

def read_airport_covid_cases():
    pass
