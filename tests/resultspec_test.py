import pytest
import os

from hdat.resultspec import resolve_resultspecs
from hdat.suite import collect_suites
from hdat.util import AbortError, repository_root


@pytest.fixture
def suites():
    yield collect_suites(repository_root(os.getcwd()))


class TestResolveResultSpec:
    def test_existing_file(self, archive, suites, mock_results):
        resultspec = archive._result_filename('a', '1', 'r1')
        assert list(resolve_resultspecs(archive, suites, resultspec)) == [mock_results[0]]

    @pytest.mark.skip
    def test_existing_file_invalid(self, archive):
        # TODO: test how the resolver handles invalid files
        pass

    def test_nonexistant_file(self, archive, suites):
        resultspec = archive._result_filename('a', '1', 'huh')
        with pytest.raises(AbortError):
            resolve_resultspecs(archive, suites, resultspec)

    def test_fully_qualified(self, archive, suites, mock_results):
        resultspec = 'a/1/101_r2'
        assert list(resolve_resultspecs(archive, suites, resultspec)) == [mock_results[1]]

    def test_relative_index_1(self, archive, suites, mock_results):
        resultspec = 'a/1/~0'
        assert list(resolve_resultspecs(archive, suites, resultspec)) == [mock_results[1]]

    def test_relative_index_2(self, archive, suites, mock_results):
        resultspec = 'a/1/~1'
        assert list(resolve_resultspecs(archive, suites, resultspec)) == [mock_results[0]]

    def test_relative_index_3(self, archive, suites, mock_results):
        resultspec = 'a/1/~2'
        with pytest.raises(AbortError):
            assert resolve_resultspecs(archive, suites, resultspec)

    def test_fully_qualified_missing(self, archive, suites):
        resultspec = 'a/1/huh'
        with pytest.raises(AbortError):
            resolve_resultspecs(archive, suites, resultspec)

    def test_most_recent_in_case(self, archive, suites, mock_results):
        resultspec = 'a/1'
        assert list(resolve_resultspecs(archive, suites, resultspec)) == [mock_results[1]]

    def test_most_recent_in_suite(self, archive, suites, mock_results):
        resultspec = 'a'
        assert list(resolve_resultspecs(archive, suites, resultspec)) == [mock_results[1], mock_results[2]]

    def test_most_recent_all(self, archive, suites, mock_results):
        resultspec = ''
        results = list(resolve_resultspecs(archive, suites, resultspec))
        assert results == [mock_results[1], mock_results[2], mock_results[3]]

    def test_most_recent_missing(self, archive, suites):
        resultspec = 'a/huh'
        assert 'does not exist' in resolve_resultspecs(archive, suites, resultspec)
