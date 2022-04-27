import argparse
from concurrent import futures
import os

import dotenv
import grpc

from grpc_interceptor import ExceptionToStatusInterceptor
import authentication_pb2_grpc
from authentication_pb2 import (
    AuthenticationResponse
)


class AuthenticationService(authentication_pb2_grpc.AuthenticationServicer):


    def Authenticate(self, request, context):
        granted = request.username == os.environ['USERNAME'] and request.password == os.environ['PASSWORD']
        return AuthenticationResponse(granted=granted)


def serve():
    interceptors = [ExceptionToStatusInterceptor()]

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
    )

    authentication_pb2_grpc.add_AuthenticationServicer_to_server(
        AuthenticationService(), server
    )

    server.add_insecure_port("[::]:{}".format(os.environ['OUT_PORT']))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    if not 'USERNAME' and not 'PASSWORD' in os.environ:
        argparser = argparse.ArgumentParser()
        argparser.add_argument('--env', '-e')
        arguments = argparser.parse_args()
        env_path = arguments.env if arguments.env else '.env'
        dotenv.load_dotenv(arguments.env)
    serve()
