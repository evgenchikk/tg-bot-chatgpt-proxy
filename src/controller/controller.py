from abc import ABC

from service import Service


class Controller(ABC):
    def __init__(self, service: Service):
        self.service = service

    def run(self):
        pass
