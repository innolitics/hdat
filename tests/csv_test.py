import pytest

import hdat.reports as reports
import hdat.hdat_cli as hdat


@pytest.fixture
def nested_result():
    return {
        "case_id": "cid",
        "commit": "c1",
        "metrics": {
            "max": 100,
            "mean": 50,
            "min": 1,
            "size": 100,
            "std": 3
        },
        "ran_on": 123.456,
        "result_id": "r1",
        "status": "pass",
        "suite_id": "mock_suite"
    }


class TestNestedItems:
    def test_non_nested_key(self, nested_result):
        assert reports.get_nested_item(nested_result, ['case_id']) == 'cid'

    def test_nested_key(self, nested_result):
        assert reports.get_nested_item(nested_result, ['metrics', 'max']) == 100

    def test_nested_key_not_in_result(self, mock_results):
        assert reports.get_nested_item(mock_results[0], ['metrics', 'max']) is None

    def test_nested_key_non_nested_result(self):
        mock_non_nested_result = {
            "case_id": "cid",
            "commit": "c1",
            "metrics": 10,
            "ran_on": 123.456,
            "result_id": "r1",
            "status": "pass",
            "suite_id": "mock_suite"
        }

        assert reports.get_nested_item(mock_non_nested_result, ['metrics', 'max']) is None


class TestPrintResult:
    def test_print_default(self, nested_result, capfd):
        hdat.print_results([nested_result], '')
        out, err = capfd.readouterr()
        assert 'case_id,commit,metrics.max,metrics.mean' in out
        assert 'cid,c1,100,50,1,100,3,123.456,r1' in out

    def test_non_existing_keys(self, nested_result, capfd):
        hdat.print_results([nested_result], 'case_id, wrong.nestedkey, wrongkey')
        out, err = capfd.readouterr()
        assert 'case_id,wrong.nestedkey,wrongkey' in out

    def test_quoted_key(self, nested_result, capfd):
        hdat.print_results([nested_result], 'case_id, "quotedkey"')
        out, err = capfd.readouterr()
        assert '"""quotedkey""",case_id' in out

    def test_space_in_key(self, nested_result, capfd):
        hdat.print_results([nested_result], 'case_id, space key, commit')
        out, err = capfd.readouterr()
        assert 'case_id,commit,space key' in out
