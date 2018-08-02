import pytest

from hdat.util import AbortError


class TestResolveResultSpec:
    def test_existing_file(self, archive, mock_results):
        resultspec = archive._result_filename('a', '1', 'r1')
        assert list(archive.resolve_resultspec(resultspec)) == [mock_results[0]]

    @pytest.mark.skip
    def test_existing_file_invalid(self, archive):
        # TODO: test how the resolver handles invalid files
        pass

    def test_nonexistant_file(self, archive):
        resultspec = archive._result_filename('a', '1', 'huh')
        with pytest.raises(AbortError):
            archive.resolve_resultspec(resultspec)

    def test_fully_qualified(self, archive, mock_results):
        resultspec = 'a/1/101_r2'
        assert list(archive.resolve_resultspec(resultspec)) == [mock_results[1]]

    def test_relative_index_1(self, archive, mock_results):
        resultspec = 'a/1/~0'
        assert list(archive.resolve_resultspec(resultspec)) == [mock_results[1]]

    def test_relative_index_2(self, archive, mock_results):
        resultspec = 'a/1/~1'
        assert list(archive.resolve_resultspec(resultspec)) == [mock_results[0]]

    def test_relative_index_3(self, archive, mock_results):
        resultspec = 'a/1/~2'
        with pytest.raises(AbortError):
            assert archive.resolve_resultspec(resultspec)

    def test_fully_qualified_missing(self, archive):
        resultspec = 'a/1/huh'
        with pytest.raises(AbortError):
            archive.resolve_resultspec(resultspec)

    def test_most_recent_in_case(self, archive, mock_results):
        resultspec = 'a/1'
        assert list(archive.resolve_resultspec(resultspec)) == [mock_results[1]]

    def test_most_recent_in_suite(self, archive, mock_results):
        resultspec = 'a'
        assert list(archive.resolve_resultspec(resultspec)) == [mock_results[1], mock_results[2]]

    def test_most_recent_all(self, archive, mock_results):
        resultspec = ''
        results = list(archive.resolve_resultspec(resultspec))
        assert results == [mock_results[1], mock_results[2], mock_results[3]]

    def test_most_recent_missing(self, archive):
        resultspec = 'a/huh'
        try:
            archive.resolve_resultspec(resultspec)
        except AbortError as e:
            assert 'the case "huh" does not exist within suite "a"' in str(e)

    def test_unused_case_all(self, unused_case_archive):
        resultspec = ''
        results = unused_case_archive.resolve_resultspec(resultspec)
        try:
            for result in results:
                print(result)
        except AbortError as e:
            assert 'no result recorded' in str(e)

    def test_unused_case(self, unused_case_archive):
        resultspec = 'a/2'
        try:
            unused_case_archive.resolve_resultspec(resultspec)
        except AbortError as e:
            assert 'no result recorded' in str(e)
