from datetime import date
import grpc

from data_delivery_pb2 import Airport, AirportRequest, FlightRequest, CovidCasesRequest, AirportCovidCaseRequest
from data_delivery_pb2_grpc import DataDeliveryStub

data_delivery_channel = grpc.insecure_channel('localhost:50051')
data_delivery_client = DataDeliveryStub(data_delivery_channel)

def read_all_airports(continent, airport_type):
    request = AirportRequest(
        continent=continent
    )
    response = data_delivery_client.Airports(request)
    return response

def read_all_flights(date, continent):
    request = FlightRequest(
        date=date,
        continent=continent
    )
    response = data_delivery_client.Flights(request)
    return response

def read_all_covid_cases(date, area_level):
    request = CovidCasesRequest(
        date=date,
        area_level=area_level
    )
    response = data_delivery_client.CovidCases(request)
    return response

def read_airport_covid_cases(airport_code, area_level):
    request = AirportCovidCaseRequest(
        airport_code=airport_code,
        area_level=area_level
    )
    response = data_delivery_client.AirportCovidCases(request)
    return response
