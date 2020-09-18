from pypelinerr import Pipeline
from schema import Schema


class TestPipeline(Pipeline):

    def phases(self):
        return [
            'phase_one',
            'phase_tpl',
            'phase_three'
        ]

    def phase_one(self):
        self.options['option_for_second_phase'] = True

    def phase_tpl(self):
        if 'option_for_second_phase' in self.options:
            return 'an option got passed from first phase, cool!'

    def phase_three(self):
        self.options['reached_third_phase'] = True

    def phase_test_break(self):
        if 'some_option' not in self.options:
            self.break_operation()

    def phase_test_fail(self):
        if 'another_option' not in self.options:
            self.fail_phase()


def run_pipeline(initial_options=None, phases=None, entry_phase=None, schema=None):
    pl = TestPipeline(options=initial_options if initial_options else {}, entry_phase=entry_phase, schema=schema)
    if phases:
        pl.phases = lambda: phases
    return pl.run()


def test_happy_trail():
    pl = run_pipeline()
    assert pl.success is True
    assert 'option_for_second_phase' in pl.options
    assert 'reached_third_phase' in pl.options


def test_break_operation():
    phases_with_break = ['phase_one', 'phase_tpl', 'phase_test_break', 'phase_three']
    pl = run_pipeline(initial_options={'initial_option_1': 1}, phases=phases_with_break)
    assert pl.success is True
    assert 'option_for_second_phase' in pl.options
    assert pl.break_phase == 'phase_test_break'
    assert 'reached_third_phase' not in pl.options


def test_fail_operation():
    phases_with_fail = ['phase_one', 'phase_tpl', 'phase_test_fail', 'phase_three']
    pl = run_pipeline(initial_options={'initial_option_1': 1}, phases=phases_with_fail)
    assert pl.success is False
    assert pl.fail_traceback is not None
    assert pl.fail_message is not None
    assert 'option_for_second_phase' in pl.options
    assert pl.fail_phase == 'phase_test_fail'
    assert 'reached_third_phase' not in pl.options


def test_entry_phase():
    pl = run_pipeline(initial_options={'some_initial_options': 1}, entry_phase='phase_three')
    assert pl.success is True
    assert 'option_for_second_phase' not in pl.options
    assert 'reached_third_phase' in pl.options


class TestSchemaValidation:

    class TestWhenSchemaIsValid:
        @staticmethod
        def test_it_should_run_phase_successfully():
            schema = Schema({'user_id': int, 'logged_in': bool})
            event_payload = {'user_id': 123, 'logged_in': True}
            pl = run_pipeline(initial_options=event_payload, schema=schema)
            assert pl.success is True

    class TestWhenSchemaIsInvalid:
        @staticmethod
        def test_it_should_fail_operation_immediately():
            schema = Schema({'user_id': int, 'logged_in': bool})
            event_payload = {'user_id': 'not a number', 'logged_in': True}
            pl = run_pipeline(initial_options=event_payload, schema=schema)
            assert pl.success is False
            assert pl.fail_traceback is not None
            assert 'option_for_second_phase' not in pl.options
