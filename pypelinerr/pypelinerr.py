from abc import ABC, abstractmethod
from time import time
from traceback import format_exc
from typing import Dict, List, Optional, AnyStr

from schema import Schema, SchemaError


class Pipeline(ABC):
    def __init__(self, options: Dict = None, entry_phase: str = None, schema: Optional[Schema] = None):
        self.operation_time = time()
        self.options = options if options else {}
        self._entry_phase = entry_phase
        self.schema: Optional[Schema] = schema
        self.current_phase = None
        self.break_phase = None
        self.fail_phase = None
        self.success = False
        self.fail_traceback: Optional[str] = None
        self.fail_message: Optional[str] = None

    def run(self):
        try:
            if self.schema:
                self.schema.validate(self.options)
            self._run_phases()
        except SchemaError as e:
            self.on_exception(exception=e)
        except Exception as e:
            if self.success:
                self.break_phase = self.current_phase
            else:
                self.on_exception(exception=e)

        self.operation_time = time() - self.operation_time
        return self

    def _run_phases(self):
        phases = self.phases()
        if self._entry_phase:
            start_phase = phases.index(self._entry_phase)
            phases = phases[start_phase:]
        for phase in phases:
            self.current_phase = phase
            getattr(self, phase)()
        self.success = True

    @abstractmethod
    def phases(self) -> List[str]:
        raise NotImplementedError

    def break_operation(self, message: Optional[AnyStr] = None):
        self.success = True
        raise Exception(message)

    def fail_operation(self, message: Optional[AnyStr] = None):
        self.success = False
        raise Exception(message)

    def on_exception(self, exception: Optional[Exception] = None):
        self.fail_phase = self.current_phase
        self.fail_traceback = format_exc()
        self.fail_message = str(exception) if exception else None
