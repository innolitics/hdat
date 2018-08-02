import pytest

from hdat.hdat_cli import hdat_cli
from hdat.util import AbortError


@pytest.fixture
def hdat_cli_with_mocks(mock_suites, tmp_golden_store, tmp_archive, mock_git_info):
    return lambda args: hdat_cli(args, mock_suites, tmp_golden_store, tmp_archive, mock_git_info)


class TestMainRun:
    def test_run_all(self, hdat_cli_with_mocks):
        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['run'])
        assert 'UNKNOWN: 3' in str(e)

    def test_runshow(self, hdat_cli_with_mocks):
        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['runshow', 'a'])
        assert 'showing "a/1' in str(e)

    def test_show_most_recent(self, hdat_cli_with_mocks):
        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['run', 'a/1'])

        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['show', 'a/1'])

        assert 'showing "a/1' in str(e)

    def test_diff(self, hdat_cli_with_mocks, archive, mock_results):
        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['diff', 'a/1/r1', 'a/1/101_r2'])

        assert 'diffing "a/1/r1" and "a/1/101_r2"' in str(e)
