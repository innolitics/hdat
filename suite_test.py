import pytest


@pytest.fixture
def mock_suite(tmp_golden_store, tmp_archive, mock_git_info, basic_suite_a):
    return basic_suite_a(tmp_golden_store, tmp_archive, mock_git_info)


class TestAlgorithmRunnerTestSuite:
    def test_run_case_with_no_golden(self, mock_suite, tmp_archive):
        suite_id = 'a'
        case_id = '1'

        assert len(tmp_archive.select_all(suite_id, case_id)) == 0

        passed = mock_suite.run_case(case_id)

        assert passed == False
        assert len(tmp_archive.select_all(suite_id, case_id)) == 1

    def test_run_case_with_golden(self, mock_suite, tmp_archive, tmp_golden_store):
        suite_id = 'a'
        case_id = '1'

        result_id = '1234-commit'
        mock_golden_result = {
            'case_id': case_id,
            'suite_id': suite_id,
            'result_id': result_id,
            'metrics': 10,
        }

        tmp_golden_store.insert(mock_golden_result)

        assert len(tmp_archive.select_all(suite_id, case_id)) == 0

        passed = mock_suite.run_case(case_id)

        assert passed == True
        assert len(tmp_archive.select_all(suite_id, case_id)) == 1
