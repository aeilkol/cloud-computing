import pytest
import datetime
import os

import data_analysis
from data_analysis_pb2 import (
    AirportAnalysisRequest,
    AirportAnalysisResponse
)
from data_delivery_pb2 import (
    AirportCovidCaseResponse,
    FlightsByDateResponse
)


class TestDataAnalysis:

    def test_AirportAnalysis(self):
        def mock_airport_covid_case_request(*args, **kwargs):
            return AirportCovidCaseResponse(
                incidences=[{'incidence': 175.85503, 'date': str(datetime.date(2020, 4, 10))},
                    {'incidence': 172.23662, 'date': str(datetime.date(2020, 4, 11))},
                    {'incidence': 154.14453, 'date': str(datetime.date(2020, 4, 12))},
                    {'incidence': 142.5656, 'date': str(datetime.date(2020, 4, 13))},
                    {'incidence': 138.2235, 'date': str(datetime.date(2020, 4, 14))},
                    {'incidence': 125.92088, 'date': str(datetime.date(2020, 4, 15))}],
                airport_code='EDDM',
                region='DE21A'
            )


        def mock_flights_by_date_request(*args, ** kwargs):
            return FlightsByDateResponse(
                flights=[{'date': str(datetime.date(2019, 4, 10)), 'count': 46},
                    {'date': str(datetime.date(2019, 4, 11)), 'count': 40},
                    {'date': str(datetime.date(2019, 4, 12)), 'count': 48},
                    {'date': str(datetime.date(2019, 4, 13)), 'count': 48},
                    {'date': str(datetime.date(2019, 4, 14)), 'count': 47},
                    {'date': str(datetime.date(2019, 4, 15)), 'count': 45},
                    {'date': str(datetime.date(2020, 4, 10)), 'count': 2},
                    {'date': str(datetime.date(2020, 4, 11)), 'count': 2},
                    {'date': str(datetime.date(2020, 4, 12)), 'count': 1},
                    {'date': str(datetime.date(2020, 4, 13)), 'count': 1},
                    {'date': str(datetime.date(2020, 4, 14)), 'count': 7},
                    {'date': str(datetime.date(2020, 4, 15)), 'count': 2}
                ]
            )
        os.environ['DATA_DELIVERY_ADDRESS'] = 'TEST'
        os.environ['DATA_DELIVERY_PORT'] = '123'

        service = data_analysis.DataAnalysisService()
        service.data_delivery_client.AirportCovidCases = mock_airport_covid_case_request
        service.data_delivery_client.FlightsByDate = mock_flights_by_date_request
        request = AirportAnalysisRequest(airport_code='EDDM')
        response = service.AirportAnalysis(request, None)
        assert type(response) == AirportAnalysisResponse
        assert len(response.analysis) == 6
