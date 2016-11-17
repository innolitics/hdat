import pytest

from hdatt.main import main
from hdatt.util import AbortError


@pytest.fixture
def main_with_mocks(mock_suites, tmp_golden_store, tmp_archive, mock_git_info):
    return lambda args: main(args, mock_suites, tmp_golden_store, tmp_archive, mock_git_info)


class TestMainRun:
    def test_run_all_verify_all_rerun(self, main_with_mocks):
        with pytest.raises(AbortError) as e:
            main_with_mocks(['run'])
        assert '3 of 3' in str(e)

        main_with_mocks(['verify', 'a/1'])

        with pytest.raises(AbortError) as e:
            main_with_mocks(['run'])
        assert '2 of 3' in str(e)

        main_with_mocks(['verify', 'a/2'])
        main_with_mocks(['verify', 'b/3'])

        main_with_mocks(['run'])

    def test_show_most_recent(self, main_with_mocks, capsys):
        with pytest.raises(AbortError) as e:
            main_with_mocks(['run', 'a/1'])

        with pytest.raises(AbortError) as e:
            main_with_mocks(['show'])

        _, err = capsys.readouterr()
        assert 'showing "a/1' in str(err)

    # def test_diff(self):
        # pass
