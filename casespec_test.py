import pytest

from hdatt.casespec import resolve_casespecs
from hdatt.util import AbortError


class TestSelectCases:
    def test_select_all(self, mock_suites):
        assert set(resolve_casespecs(mock_suites, [''])) == set([('a', '1'), ('a', '2'), ('b', '3')])

    def test_select_suite_a(self, mock_suites):
        assert resolve_casespecs(mock_suites, ['a']) == [('a', '1'), ('a', '2')] 

    def test_collect_order_preserved(self, mock_suites):
        assert resolve_casespecs(mock_suites, ['b', 'a']) == [('b', '3'), ('a', '1'), ('a', '2')] 

    def test_select_case(self, mock_suites):
        assert resolve_casespecs(mock_suites, ['a.1']) == [('a', '1')] 

    def test_duplicates_removed(self, mock_suites):
        assert resolve_casespecs(mock_suites, ['a.2', 'a']) == [('a', '2'), ('a', '1')] 

    def test_unknown_suite(self, mock_suites):
        with pytest.raises(AbortError):
            resolve_casespecs(mock_suites, ['c'])

    def test_unknown_case(self, mock_suites):
        with pytest.raises(AbortError):
            resolve_casespecs(mock_suites, ['b.4'])

    def test_long_specifier(self, mock_suites):
        with pytest.raises(AbortError):
            resolve_casespecs(mock_suites, ['a.1.huh'])

