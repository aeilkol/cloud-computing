import os
import logging
import argparse
from concurrent import futures

import dotenv
import grpc

from grpc_interceptor import ExceptionToStatusInterceptor

import logging_pb2_grpc
from logging_pb2 import LogResponse, Service


class LoggingService(logging_pb2_grpc.LoggingServiceServicer):

    def __init__(self):

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        if os.path.exists(os.environ['LOG_PATH']):
            if os.path.isfile(os.environ['LOG_PATH']):
                raise ValueError('LOG_PATH exists already and is a file')
        else:
            os.makedirs(os.environ['LOG_PATH'])

        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(origin)s:%(message)s')

        self.main_logger = logging.getLogger('main')
        self.main_logger.setLevel(logging.INFO)
        main_file_handler = logging.FileHandler(f'{os.environ["LOG_PATH"]}/main.log')
        main_file_handler.setFormatter(formatter)
        self.main_logger.addHandler(main_file_handler)

        self.outbound_logger = logging.getLogger('outbound')
        self.outbound_logger.setLevel(logging.INFO)
        outbound_file_handler = logging.FileHandler(f'{os.environ["LOG_PATH"]}/outbound.log')
        outbound_file_handler.setFormatter(formatter)
        self.outbound_logger.addHandler(outbound_file_handler)

        self.data_delivery_logger = logging.getLogger('data_delivery')
        self.data_delivery_logger.setLevel(logging.INFO)
        data_delivery_file_handler = logging.FileHandler(f'{os.environ["LOG_PATH"]}/data_delivery.log')
        data_delivery_file_handler.setFormatter(formatter)
        self.data_delivery_logger.addHandler(data_delivery_file_handler)

        self.data_analysis_logger = logging.getLogger('data_analysis')
        self.data_analysis_logger.setLevel(logging.INFO)
        data_analysis_file_handler = logging.FileHandler(f'{os.environ["LOG_PATH"]}/data_analysis.log')
        data_analysis_file_handler.setFormatter(formatter)
        self.data_analysis_logger.addHandler(data_analysis_file_handler)

        self.administrator_analysis_logger = logging.getLogger('administrator_analysis')
        self.administrator_analysis_logger.setLevel(logging.INFO)
        administrator_analysis_file_handler = logging.FileHandler(f'{os.environ["LOG_PATH"]}/administrator_analysis.log')
        administrator_analysis_file_handler.setFormatter(formatter)
        self.administrator_analysis_logger.addHandler(administrator_analysis_file_handler)

        self.error_logger = logging.getLogger('error')
        self.error_logger.setLevel(logging.ERROR)
        error_file_handler = logging.FileHandler(f'{os.environ["LOG_PATH"]}/error.log')
        error_file_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_file_handler)

    def Log(self, request, context):

        message = request.message
        if len(message) == 0 or message.isspace():
            return LogResponse(logged=False)
        if message.endswith('\n'):
            message = message[:-1]

        level = request.level * 10 + 10
        origin = Service.Name(request.origin)
        print(f'Received message from {origin}')
        self.main_logger.log(level, message, extra={'origin': origin})
        if request.origin == 0:  # 'outbound'
            self.outbound_logger.log(level, message, extra={'origin': origin})
        elif request.origin == 1:  # 'data_delivery'
            self.data_delivery_logger.log(level, message, extra={'origin': origin})
        elif request.origin == 2:  # 'data_analysis'
            self.data_analysis_logger.log(level, message, extra={'origin': origin})
        elif request.origin == 3:  # 'administrator_analysis'
            self.administrator_analysis_logger.log(level, message, extra={'origin': origin})
        else:  # should not be reached because of service enum
            self.main_logger.log(3, f'Unknown origin service {request.origin}', extra={'origin': 'logging_service'})

        if level >= 30:
            self.error_logger.log(level, message, extra={'origin': origin})

        return LogResponse(logged=True)


def serve():

    interceptors = [ExceptionToStatusInterceptor()]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    logging_pb2_grpc.add_LoggingServiceServicer_to_server(
        LoggingService(), server
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
    serve()
