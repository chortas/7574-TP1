import signal
import logging

class GracefulStopper:
    def __init__(self):
        self.stop = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.stop = True

    def exit_gracefully(self):
        self.stop = True
    
    def has_been_stopped(self):
        return self.stop
