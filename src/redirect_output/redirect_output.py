import sys
import logging

from logging_pb2 import LogRequest


class LoggingRedirector:

    def __init__(self, logging_client, origin, stdout=True):

        self.logging_client = logging_client
        self.origin = origin
        self.file_out = open('log.txt', 'a')

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
            self.file_out.write(txt + '\n')
            self.original_stdout.write(txt + '\n')
            try:
                request = LogRequest(message=txt, level=level, origin=self.origin)
                self.logging_client.Log(request)
            except Exception as e:
                self.original_stdout.write('Logging service not reachable')
                raise e

    def flush(self):
            self.file_out.flush()
            self.original_stdout.flush()
