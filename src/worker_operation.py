from time import time
from traceback import format_exc


class WorkerOperation:
    def __init__(self, options={}):
        self.operation_time = time()
        self.options = options
        self.current_phase = None
        self.break_phase = None
        self.fail_phase = None
        self.success = False
        self.fail_traceback = None

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

    def phases(self):
        NotImplementedError()

    def break_operation(self, message=None):
        self.success = True
        raise Exception(message)

    def fail_operation(self, message=None):
        self.success = False
        raise Exception(message)
