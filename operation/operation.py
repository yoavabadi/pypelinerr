from abc import ABC, abstractmethod
from time import time
from traceback import format_exc
from typing import List

from schema import Schema


class Operation(ABC):
    def __init__(self, options=None, entry_phase=None, schema: Schema = None):
        self.schema = schema
        self.options = options if options else {}
        self.operation_time = time()
        self._entry_phase = entry_phase
        self.current_phase = None
        self.break_phase = None
        self.fail_phase = None
        self.success = False
        self.fail_traceback = None
        self.fail_message = None

    def run(self):
        if self.schema:
            self.schema.validate(self.options)
        try:
            self._run_phases()
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
    def phases(self) -> List[str]:
        raise NotImplemented

    def break_operation(self, message=None):
        self.success = True
        raise Exception(message)

    def fail_operation(self, message=None):
        self.success = False
        raise Exception(message)

    def _run_phases(self):
        phases = self.phases()
        if self._entry_phase:
            start_phase = phases.index(self._entry_phase)
            phases = phases[start_phase:]
        for phase in phases:
            self.current_phase = phase
            getattr(self, phase)()
        self.success = True
