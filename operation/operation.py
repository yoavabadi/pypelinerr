from abc import ABC, abstractmethod
from time import time
from traceback import format_exc
from typing import Iterable


class Operation(ABC):
    def __init__(self, options=None):
        self.options = options if options else {}
        self.operation_time = time()
        self.current_phase = None
        self.break_phase = None
        self.fail_phase = None
        self.success = False
        self.fail_traceback = None
        self.fail_message = None

    def run(self):
        try:
            for phase in self.phases():
                self.current_phase = phase
                getattr(self, phase)()
            self.success = True
        except Exception as e:
            if self.success:
                self.break_phase = self.current_phase
            else:
                self.fail_phase = self.current_phase
                self.fail_message = e
                self.fail_traceback = format_exc()

        self.operation_time = time() - self.operation_time
        return self

    @abstractmethod
    def phases(self) -> Iterable[str]:
        raise NotImplemented

    def break_operation(self, message=None):
        self.success = True
        raise Exception(message)

    def fail_operation(self, message=None):
        self.success = False
        raise Exception(message)
