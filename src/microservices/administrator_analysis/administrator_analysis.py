import time
import os
import argparse
import sys
from concurrent import futures

import dotenv
import psycopg2, psycopg2.extras
import grpc

from grpc_interceptor import ExceptionToStatusInterceptor

from administrator_analysis_pb2 import (
    RequestAnalysisResponse
)
import administrator_analysis_pb2_grpc

from logging_pb2_grpc import LoggingServiceStub
from redirect_output import LoggingRedirector

class AdministratorAnalysisService(administrator_analysis_pb2_grpc.AdministratorAnalysisServicer):

    def __init__(self, connection):
        self.database_service = AdministratorAnalysisDatabaseService(connection)

    def RequestAnalysis(self, request, context):
        avg_runtime = self.database_service.get_average_runtime(request.service, request.request, request.start_time,
                                                                request.end_time)
        return RequestAnalysisResponse(average_runtime=avg_runtime['avg_runtime'])


class AdministratorAnalysisDatabaseService():

    def __init__(self, connection):
        self.connection = connection

    def get_average_runtime(self, service, request, start_time=None, end_time=None):
        sql = '''
        SELECT AVG(runtime) AS avg_runtime FROM runtimes
        WHERE service = %(service)s
        AND request = %(request)s
        AND (stamp >= TO_TIMESTAMP(%(start_time)s, 'YYYY-MM-DD HH24:MI:SS+00:00') OR %(start_time)s IS NULL)
        AND (stamp >= TO_TIMESTAMP(%(end_time)s, 'YYYY-MM-DD HH24:MI:SS+00:00') OR %(end_time)s IS NULL)
        GROUP BY service, request
        '''
        params = {
            'service': service,
            'request': request,
            'start_time': start_time,
            'end_time': end_time
        }
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        return cursor.fetchone()



def serve(logging_address):

    logging_channel = grpc.insecure_channel(logging_address, options=(('grpc.enable_http_proxy', 0),))
    logging_client = LoggingServiceStub(logging_channel)

    stdout_redirector = LoggingRedirector(logging_client, 'administrator_analysis', True)
    stderr_redirector = LoggingRedirector(logging_client, 'administrator_analysis', False)

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

    interceptors = [ExceptionToStatusInterceptor()]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    administrator_analysis_pb2_grpc.add_AdministratorAnalysisServicer_to_server(
        AdministratorAnalysisService(conn), server
    )

    server.add_insecure_port("[::]:{}".format(os.environ['OUT_PORT']))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--env', '-e')
    arguments = argparser.parse_args()
    env_path = arguments.env if arguments.env else '.env'
    dotenv.load_dotenv(arguments.env)

    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        logging_host = os.environ['LOGGING_ENDPOINT_SERVICE_HOST']
        logging_port = os.environ['LOGGING_ENDPOINT_SERVICE_PORT']
    else:
        dotenv.load_dotenv(arguments.env)
        logging_host = os.environ['LOGGING_ADDRESS']
        logging_port = os.environ['LOGGING_PORT']
    logging_address = '{}:{}'.format(logging_host, logging_port)

    serve(logging_address)
