import os

from hdat.suite import collect_suites, MetricsChecker


class TestSuite:

    def test_collect_suites(self):
        test_path = os.path.dirname(__file__)
        suites = collect_suites(test_path)
        assert suites.keys() == set(['BaseSuite', 'a', 'b'])

    def test_metrics_checker_bad_keys(self):
        old = {'key1': 1}
        new = {'key2': 1}
        checker = MetricsChecker(old, new)
        assert checker.result() is False
        assert len(checker.msgs()) == 1

    def test_metrics_checker_success(self):
        old = {'float': 1.00, 'float_increase': 1.00, 'float_decrease': 1.00, 'string': 'one', 'custom': 2}
        new = {'float': 1.0000000001, 'float_increase': 1.1, 'float_decrease': 0.9, 'string': 'one', 'custom': 4}
        checker = MetricsChecker(old, new)
        checker.check_close('float')
        checker.check_can_increase('float_increase')
        checker.check_can_decrease('float_decrease')
        checker.check_exact('string')
        checker.check_custom('custom', lambda x, y: (x % 2 == 0 and y % 2 == 0, 'not even'))
        assert checker.result() is True

    def test_metrics_checker_fail(self):
        old = {'float': 1.00, 'float_increase': 1.00, 'float_decrease': 1.00, 'string': 'one', 'custom': 2}
        new = {'float': 1.01, 'float_increase': 0.89, 'float_decrease': 1.11, 'string': 'two', 'custom': 5}
        checker = MetricsChecker(old, new)
        checker.check_close('float')
        checker.check_can_increase('float_increase', abs_tol=0.1)
        checker.check_can_decrease('float_decrease', abs_tol=0.1)
        checker.check_exact('string')
        checker.check_custom('custom', lambda x, y: (x % 2 == 0 and y % 2 == 0, 'not even'))
        assert checker.result() is False
        assert len(checker.msgs()) == 5
