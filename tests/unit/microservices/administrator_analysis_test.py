import datetime

from administrator_analysis import AdministratorAnalysisService, AdministratorAnalysisDatabaseService
from administrator_analysis_pb2 import (
    RequestAnalysisRequest,
    RequestAnalysisResponse
)


class TestDataDeliveryService:

    def test_RequestAnalysis(self):
        def mock_return_db(*args, **kwargs):
            return {'avg_runtime': 2.31499214561618105960}
        AdministratorAnalysisDatabaseService.get_average_runtime = mock_return_db
        database_service = AdministratorAnalysisDatabaseService('Fake connection')
        service = AdministratorAnalysisService(database_service)
        request = RequestAnalysisRequest(service='DataAnalysis', request='AirportAnalysis')
        response = service.RequestAnalysis(request, None)
        assert type(response) == RequestAnalysisResponse
        assert type(response.average_runtime) == float
        assert response.average_runtime > 0
