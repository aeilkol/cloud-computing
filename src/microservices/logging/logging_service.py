import time
import os
import logging
import argparse
from concurrent import futures

import dotenv
import grpc

from grpc_interceptor import ExceptionToStatusInterceptor

import logging_pb2_grpc
from logging_pb2 import LoggingResponse


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):

    def __init__(self):
        #create a logger for each level that it can accept
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')

        file_handler = logging.FileHandler('test.log')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def Logging(self, request, context):
        message = request.message
        level = request.level
        self.logger.log(logging.INFO, message)

        return LoggingResponse(logged=True)


def serve():

    interceptors = [ExceptionToStatusInterceptor()]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    logging_pb2_grpc.add_LoggingServiceServicer_to_server(
        LoggingService(), server
    )

    server.add_insecure_port("[::]:50053")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    # argparser = argparse.ArgumentParser()
    # argparser.add_argument('--env', '-e')
    # arguments = argparser.parse_args()
    # env_path = arguments.env if arguments.env else '../.env'
    # dotenv.load_dotenv(arguments.env)
    serve()