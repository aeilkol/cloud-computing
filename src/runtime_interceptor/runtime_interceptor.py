import time

from grpc_interceptor import ServerInterceptor


class RuntimeInterceptor(ServerInterceptor):

    def __init__(self, connection):
        self.connection = connection

    def intercept(self, method, request, context, method_name):
        _, service, request_name = method_name.split('/')
        start_time = time.time()

        def done():
            sql = '''
            INSERT INTO runtimes (service, request, runtime)
            VALUES (%(service)s, %(request)s, %(runtime)s)
            '''
            params = {
                'service': service,
                'request': request_name,
                'runtime': time.time() - start_time
            }
            cursor = self.connection.cursor()
            cursor.execute(sql, params)
            self.connection.commit()
        context.add_callback(done)

        return method(request, context)
