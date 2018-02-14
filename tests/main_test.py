import pytest

from hdat.hdat_cli import hdat_cli
from hdat.util import AbortError


@pytest.fixture
def hdat_cli_with_mocks(mock_suites, tmp_golden_store, tmp_archive, mock_git_info):
    return lambda args: hdat_cli(args, mock_suites, tmp_golden_store, tmp_archive, mock_git_info)


class TestMainRun:
    def test_run_all_verify_all_rerun(self, hdat_cli_with_mocks):
        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['run'])
        assert 'UNKNOWN: 3' in str(e)

        hdat_cli_with_mocks(['verify', 'a/1'])

        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['run'])
        assert 'UNKNOWN: 2' in str(e)
        assert 'PASS: 1' in str(e)

        hdat_cli_with_mocks(['verify', 'a/2'])
        hdat_cli_with_mocks(['verify', 'b/3'])

        hdat_cli_with_mocks(['run'])

    def test_show_most_recent(self, hdat_cli_with_mocks):
        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['run', 'a/1'])

        with pytest.raises(AbortError) as e:
            hdat_cli_with_mocks(['show', 'a/1'])

        assert 'showing "a/1' in str(e)
