import grpc
from google.protobuf.json_format import MessageToJson

from data_delivery_pb2 import Airport, AirportRequest
from data_delivery_pb2_grpc import DataDeliveryStub

data_delivery_channel = grpc.insecure_channel('localhost:50051', options=(('grpc.enable_http_proxy', 0),))
data_delivery_client = DataDeliveryStub(data_delivery_channel)


def read_all_airports(continent, airport_type):
    request = AirportRequest(
        continent=continent,
        airport_type=airport_type
    )
    response = data_delivery_client.Airports(request)
    return MessageToJson(response)


def read_all_flights():
    pass


def read_all_covid_cases():
    pass


def read_airport_covid_cases():
    pass
