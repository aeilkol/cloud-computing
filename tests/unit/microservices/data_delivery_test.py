import datetime

from data_delivery import DataDeliveryService, DataDeliveryDatabaseService
from data_delivery_pb2 import (
    AirportRequest,
    AirportResponse,

    FlightRequest,
    FlightResponse,

    CovidCaseRequest,
    CovidCaseResponse,

    AirportCovidCaseRequest,
    AirportCovidCaseResponse,

    FlightsByDateRequest,
    FlightsByDateResponse
)


class TestDataDeliveryService:

    def test_Airports(self):
        def mock_return_db(*args, **kwargs):
            return [{'code': 'BIKF', 'name': 'Keflavik International Airport', 'type': 'large_airport',
                     'elevation': 171.0, 'continent': 'EU',
                     'location': '0101000020E61000002575029A089B36C07EC3448314FE4F40'}]
        DataDeliveryDatabaseService.get_airports = mock_return_db
        database_service = DataDeliveryDatabaseService('Fake connection')
        service = DataDeliveryService(database_service)
        request = AirportRequest(continent='EU', airport_type='large_airport')
        response = service.Airports(request, None)
        assert type(response) == AirportResponse
        assert len(response.airports) == 1
        assert len(response.airports[0].code) == 4
        assert type(response.airports[0].name) == str

    def test_Flights(self):
        def mock_return_db(*args, **kwargs):
            return [{'origin': 'BIKF', 'destination': 'EKCH', 'cardinality': 1},
                    {'origin': 'BIKF', 'destination': 'EPWR', 'cardinality': 1},
                    {'origin': 'BIKF', 'destination': 'LFPG', 'cardinality': 1},
                    {'origin': 'EBBR', 'destination': 'EDDM', 'cardinality': 1},
                    {'origin': 'EBBR', 'destination': 'EDDP', 'cardinality': 2}]

        DataDeliveryDatabaseService.get_flights = mock_return_db
        database_service = DataDeliveryDatabaseService('Fake connection')
        service = DataDeliveryService(database_service)
        request = FlightRequest(continent='EU', date='2020-01-01')
        response = service.Flights(request, None)
        assert type(response) == FlightResponse
        assert len(response.flights) == 5
        for flight in response.flights:
            assert flight.src is not None
            assert flight.dest is not None
            assert flight.cardinality is not None
            assert type(flight.src) == str
            assert len(flight.src) == 4
            assert type(flight.dest) == str
            assert len(flight.dest) == 4
            assert type(flight.cardinality) == int

    def test_CovidCases(self):
        def mock_return_db(self, *args, **kwargs):
            return [{'id': 365, 'region_id': 'DK011', 'date': datetime.date(2021, 1, 1), 'incidence': 710.4648},
                    {'id': 1202, 'region_id': 'DK012', 'date': datetime.date(2021, 1, 1), 'incidence': 827.90814},
                    {'id': 2036, 'region_id': 'DK013', 'date': datetime.date(2021, 1, 1), 'incidence': 633.4844},
                    {'id': 2868, 'region_id': 'DK014', 'date': datetime.date(2021, 1, 1), 'incidence': 161.68558},
                    {'id': 3683, 'region_id': 'DK021', 'date': datetime.date(2021, 1, 1), 'incidence': 591.53894}]

        DataDeliveryDatabaseService.get_covid_cases = mock_return_db
        database_service = DataDeliveryDatabaseService('Fake connection')
        service = DataDeliveryService(database_service)
        request = CovidCaseRequest(date='2021-01-01', area_level=0)
        response = service.CovidCases(request, None)
        assert type(response) == CovidCaseResponse
        assert len(response.covid_cases) == 5
        for covid_case in response.covid_cases:
            assert covid_case.region is not None
            assert covid_case.date is not None

    def test_AirportCovidCase(self):
        def mock_return_db(*args, **kwargs):
            return {
                'region_id': 'DE21A',
                'incidences': [{'incidence': None, 'date': datetime.date(2020, 3, 10)},
                                {'incidence': None, 'date': datetime.date(2020, 3, 9)},
                                {'incidence': 26.776281, 'date': datetime.date(2020, 8, 15)},
                                {'incidence': 26.776281, 'date': datetime.date(2020, 8, 16)},
                                {'incidence': 26.776281, 'date': datetime.date(2020, 8, 17)}]
            }


        DataDeliveryDatabaseService.get_airport_covid_cases = mock_return_db
        database_service = DataDeliveryDatabaseService('Fake connection')
        service = DataDeliveryService(database_service)
        request = AirportCovidCaseRequest(airport_code='EDDM')
        response = service.AirportCovidCases(request, None)
        assert type(response) == AirportCovidCaseResponse
        assert len(response.incidences) == 5
        assert response.region is not None
        for incidence in response.incidences:
            assert incidence.date is not None

    def test_FlightsByDate(self):
        def mock_return_db(*args, **kwargs):
            return [{'date': datetime.date(2019, 1, 1), 'count': 30},
                    {'date': datetime.date(2019, 1, 2), 'count': 37},
                    {'date': datetime.date(2019, 1, 3), 'count': 33},
                    {'date': datetime.date(2019, 1, 4), 'count': 32},
                    {'date': datetime.date(2019, 1, 5), 'count': 35}]

        DataDeliveryDatabaseService.get_flights_by_date = mock_return_db
        database_service = DataDeliveryDatabaseService('Fake connection')
        service = DataDeliveryService(database_service)
        request = FlightsByDateRequest(airport_code='EDDM', origin=True)
        response = service.FlightsByDate(request, None)
        assert type(response) == FlightsByDateResponse
        assert len(response.flights) == 5
        for flight in response.flights:
            assert flight.date is not None
            assert flight.count is not None
