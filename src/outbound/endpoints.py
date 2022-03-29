import grpc

from data_delivery_pb2 import AirportRequest, CovidCaseRequest, FlightRequest
from data_delivery_pb2_grpc import DataDeliveryStub
from google.protobuf.json_format import MessageToDict

data_delivery_channel = grpc.insecure_channel('localhost:50051', options=(('grpc.enable_http_proxy', 0),))
data_delivery_client = DataDeliveryStub(data_delivery_channel)


def read_all_airports(continent, airport_type):
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


def read_airport_covid_cases():
    pass
