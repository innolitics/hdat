import hdat.hdat_cli as hdat


class TestGetSingleCase:
    def test_default(self, mock_results):
        in_keys = ['case_id', 'result_id', 'ran_on', 'gith_hash', 'metrics.*']

        assert hdat.get_result_data(mock_results[0], in_keys) == (
            ['case_id', 'result_id', 'ran_on', 'gith_hash', 'metrics.*'],
            ['1', 'r1', 100, ' ', ' '],
            ['gith_hash', 'metrics.*']
        )

    def test_specific_metrics(self, mock_results):
        in_keys = ['case_id', 'result_id', 'metrics.mean', 'metrics.std']

        assert hdat.get_result_data(mock_results[0], in_keys) == (
            ['case_id', 'result_id', 'metrics.mean', 'metrics.std'],
            ['1', 'r1', ' ', ' '],
            ['metrics.mean', 'metrics.std']
        )

    def test_with_metrics(self):
        mock_results = {
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
        in_keys = ['case_id', 'result_id', 'ran_on', 'status', 'metrics.*']

        assert hdat.get_result_data(mock_results, in_keys) == (
            [
                'case_id', 'result_id', 'ran_on',
                'status', 'metrics.max', 'metrics.mean',
                'metrics.min', 'metrics.size', 'metrics.std'
            ],
            ['cid', 'r1', 123.456, 'pass', 100, 50, 1, 100, 3],
            []
        )


class TestPrintResult:
    def test_print_default(self, mock_results, capfd):
        hdat.print_result(mock_results[0], None)
        out, err = capfd.readouterr()
        assert out == 'case_id, result_id, ran_on, gith_hash, metrics.*\n1, r1, 100,  ,  \n'
        assert 'gith_hash' in err and 'metrics.*' in err

    def test_print_no_err(self, mock_results, capfd):
        hdat.print_result(mock_results[0], 'suite_id,case_id,result_id,ran_on')
        out, err = capfd.readouterr()
        assert out == 'suite_id, case_id, result_id, ran_on\na, 1, r1, 100\n'
        assert err == ''
