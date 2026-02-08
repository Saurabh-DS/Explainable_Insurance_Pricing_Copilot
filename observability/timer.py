import time
from contextlib import contextmanager

class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = 0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return self.duration

@contextmanager
def measure_time():
    t = Timer()
    t.start()
    yield t
    t.stop()
