from operation import Operation


class TestOperation(Operation):

    def phases(self):
        return [
            'phase_one',
            'phase_two',
            'phase_three'
        ]

    def phase_one(self):
        self.options['option_for_second_phase'] = True

    def phase_two(self):
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


def run_operation(initial_options={}, phases=[], entry_phase=None):
    wo = TestOperation(initial_options, entry_phase)
    if phases:
        wo.phases = lambda: phases
    return wo.run()


def test_happy_trail():
    wo = run_operation()
    assert wo.success is True
    assert 'option_for_second_phase' in wo.options
    assert 'reached_third_phase' in wo.options


def test_break_operation():
    phases_with_break = ['phase_one', 'phase_two', 'phase_test_break', 'phase_three']
    wo = run_operation(initial_options={'initial_option_1': 1}, phases=phases_with_break)
    assert wo.success is True
    assert 'option_for_second_phase' in wo.options
    assert wo.break_phase is 'phase_test_break'
    assert 'reached_third_phase' not in wo.options


def test_fail_operation():
    phases_with_fail = ['phase_one', 'phase_two', 'phase_test_fail', 'phase_three']
    wo = run_operation(initial_options={'initial_option_1': 1}, phases=phases_with_fail)
    assert wo.success is False
    assert wo.fail_traceback is not None
    assert 'option_for_second_phase' in wo.options
    assert wo.fail_phase is 'phase_test_fail'
    assert 'reached_third_phase' not in wo.options


def test_entry_phase():
    wo = run_operation(initial_options={'some_initial_options': 1}, entry_phase='phase_three')
    assert wo.success is True
    assert 'option_for_second_phase' not in wo.options
    assert 'reached_third_phase' in wo.options
