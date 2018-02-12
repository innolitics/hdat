import os

import pytest

from ..resultspec import resolve_resultspec
from ..util import AbortError


@pytest.fixture
def mock_results():
    return [
        {
            'suite_id': 'a',
            'case_id': '1',
            'result_id': 'r1',
            'ran_on': 100,
        },
        {
            'suite_id': 'a',
            'case_id': '1',
            'result_id': 'r2',
            'ran_on': 101,
        },
        {
            'suite_id': 'a',
            'case_id': '2',
            'result_id': 'r3',
            'ran_on': 103,
        },
        {
            'suite_id': 'b',
            'case_id': '1',
            'result_id': 'r4',
            'ran_on': 104,
        },
    ]


@pytest.fixture
def archive(tmp_archive, mock_results):
    for result in mock_results:
        tmp_archive.insert(result)
    return tmp_archive


class TestResolveResultSpec:
    def test_existing_file(self, archive, mock_results):
        resultspec = archive._result_filename('a', '1', 'r1')
        assert resolve_resultspec(archive, resultspec) == mock_results[0]

    @pytest.mark.skip
    def test_existing_file_invalid(self, archive):
        # TODO: test how the resolver handles invalid files
        pass

    def test_nonexistant_file(self, archive):
        resultspec = archive._result_filename('a', '1', 'huh')
        with pytest.raises(AbortError):
            resolve_resultspec(archive, resultspec)

    def test_fully_qualified(self, archive, mock_results):
        resultspec = 'a/1/r2'
        assert resolve_resultspec(archive, resultspec) == mock_results[1]

    def test_fully_qualified_missing(self, archive):
        resultspec = 'a/1/huh'
        with pytest.raises(AbortError):
            resolve_resultspec(archive, resultspec)

    def test_most_recent_in_case(self, archive, mock_results):
        resultspec = 'a/1'
        assert resolve_resultspec(archive, resultspec) == mock_results[1]

    def test_most_recent_in_suite(self, archive, mock_results):
        resultspec = 'a'
        assert resolve_resultspec(archive, resultspec) == mock_results[2]

    def test_most_recent_overall(self, archive, mock_results):
        resultspec = ''
        assert resolve_resultspec(archive, resultspec) == mock_results[3]

    def test_most_recent_missing(self, archive):
        resultspec = 'a/huh'
        with pytest.raises(AbortError):
            resolve_resultspec(archive, resultspec)
