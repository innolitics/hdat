import pytest

import os

from hdat.suite import collect_suites, MetricsChecker


class TestSuite:

    def test_collect_suites(self):
        test_path = os.path.dirname(__file__)
        suites = collect_suites(test_path)
        assert suites.keys() == set(['BaseSuite', 'a', 'b'])

    def test_metrics_checker_bad_keys(self):
        old = {'key1': 1, 'key3': 'value1'}
        new = {'key2': 1, 'key3': 'value2'}
        checker = MetricsChecker(old, new)
        checker.exact('key3')
        assert checker.match() is False
        assert len(checker.msgs()) == 2  # key3 is also checked

    @pytest.mark.parametrize("old, new, method, expected", [
        ({'item': 1.00}, {'item': 1.000000001}, 'exact', False),
        ({'item': 1}, {'item': 1}, 'exact', True),
        ({'item': 1}, {'item': 2}, 'close', False),
        ({'item': 1.00}, {'item': 1.0000000001}, 'close', True),
        ({'item': 4}, {'item': 3}, 'can_increase', False),
        ({'item': 4}, {'item': 5}, 'can_increase', True),
        ({'item': 4}, {'item': 5}, 'can_decrease', False),
        ({'item': 4}, {'item': 3}, 'can_decrease', True)
    ])
    def test_checker_single(self, old, new, method, expected):
        checker = MetricsChecker(old, new)
        check_func = getattr(checker, method)
        check_func(list(old.keys())[0])
        assert checker.match() is expected and checker.result()[0] is expected

    def test_custom_check(self):
        old = {'item': 10}
        new_good = {'item': 5}
        new_bad = {'item': 4}
        checker_good = MetricsChecker(old, new_good)
        checker_bad = MetricsChecker(old, new_bad)
        checker_good.custom('item', func=lambda x, y: (x % y == 0 or y % x == 0, "no factor"))
        checker_bad.custom('item', func=lambda x, y: (x % y == 0 or y % x == 0, "no factor"))
        assert checker_good.match() is True
        assert checker_bad.match() is False

    def test_can_increase_with_tol(self):
        old = {'item': 10}
        new_good = {'item': 9}
        new_bad = {'item': 8}
        checker_good = MetricsChecker(old, new_good)
        checker_bad = MetricsChecker(old, new_bad)
        checker_good.can_increase('item', abs_tol=1)
        checker_bad.can_increase('item', abs_tol=1)
        assert checker_good.match() is True
        assert checker_bad.match() is False
        assert True

    def test_can_decrease_with_tol(self):
        old = {'item': 10}
        new_good = {'item': 11}
        new_bad = {'item': 12}
        checker_good = MetricsChecker(old, new_good)
        checker_bad = MetricsChecker(old, new_bad)
        checker_good.can_decrease('item', abs_tol=1)
        checker_bad.can_decrease('item', abs_tol=1)
        assert checker_good.match() is True
        assert checker_bad.match() is False
        assert True

    def test_metrics_checker_multi_success(self):
        old = {'float': 1.00, 'float_increase': 1.00, 'float_decrease': 1.00, 'string': 'one', 'custom': 2}
        new = {'float': 1.0000000001, 'float_increase': 1.1, 'float_decrease': 0.9, 'string': 'one', 'custom': 4}
        checker = MetricsChecker(old, new)
        checker.close('float', abs_tol=0.01)
        checker.can_increase('float_increase')
        checker.can_decrease('float_decrease')
        checker.exact('string')
        checker.custom('custom', lambda x, y: (x % 2 == 0 and y % 2 == 0, 'not even'))
        assert checker.match() is True and checker.result()[0] is True

    def test_metrics_checker_multi_fail(self):
        old = {'float': 1.00, 'float_increase': 1.00, 'float_decrease': 1.00, 'string': 'one', 'custom': 2}
        new = {'float': 1.01, 'float_increase': 0.89, 'float_decrease': 1.11, 'string': 'two', 'custom': 5}
        checker = MetricsChecker(old, new)
        checker.close('float')
        checker.can_increase('float_increase', abs_tol=0.1)
        checker.can_decrease('float_decrease', abs_tol=0.1)
        checker.exact('string')
        checker.custom('custom', lambda x, y: (x % 2 == 0 and y % 2 == 0, 'not even'))
        assert checker.match() is False and checker.result()[0] is False
        assert len(checker.msgs()) == 5
