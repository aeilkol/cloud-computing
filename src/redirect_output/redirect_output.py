import sys
from logging_pb2 import LogRequest, Service, Level


class LoggingRedirector:

    def __init__(self, logging_client, origin, stdout=True):
        self.logging_client = logging_client
        self.origin = origin
        if stdout:
            self.standard_level = 'info'
            self.original_stdout = sys.stdout
        else:
            self.standard_level = 'error'
            self.original_stdout = sys.stderr

    def write(self, txt, level=None):
        if len(txt) > 0:
            if not level:
                level = self.standard_level
            if (type(txt) == bytes):
                txt = str(txt)
            self.original_stdout.write(txt)
            self.original_stdout.write('\n')
            try:
                request = LogRequest(message=txt, level=level, origin=self.origin)
                self.logging_client.Log(request)
            except Exception as e:
                self.original_stdout.write('Logging service not reachable')
                raise e

    def flush(self):
        pass
