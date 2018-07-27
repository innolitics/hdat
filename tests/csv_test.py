import hdat.hdat_cli as hdat


class TestGetKeys:
    def test_keys_default(self, mock_results, mock_keys):
        assert hdat.get_result_keys(mock_results[0], mock_keys) == (
            ['case_id', 'ran_on', 'result_id']
        )

    def test_non_existing_keys(self, mock_results):
        in_keys = ['case_id', 'result_id', 'metrics.mean', 'metrics.std']

        assert hdat.get_result_keys(mock_results[0], in_keys) == (
            ['case_id', 'result_id']
        )

    def test_with_wildcard(self):
        mock_result = {
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

        assert hdat.get_result_keys(mock_result, in_keys) == [
            'case_id', 'metrics.max', 'metrics.mean',
            'metrics.min', 'metrics.size', 'metrics.std',
            'ran_on', 'result_id', 'status'
        ]

    def test_nested_keys(self):
        mock_result = {
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
        in_keys = ['case_id', 'metrics.max', 'metrics.mean', 'metrics.size']

        assert hdat.get_result_keys(mock_result, in_keys) == [
            'case_id', 'metrics.max', 'metrics.mean', 'metrics.size'
        ]

    def test_dot_modifier(self):
        mock_result = {
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
        in_keys = ['case_id', 'result_id', 'commit', 'metrics.']

        assert hdat.get_result_keys(mock_result, in_keys) == [
            'case_id', 'commit', 'result_id'
        ]


class TestUnusedKeys:
    def test_no_unused(self, mock_keys):
        distinct_keys = mock_keys

        assert not hdat.get_unused_keys(mock_keys, distinct_keys)

    def test_some_unused(self, mock_keys):
        distinct_keys = ['case_id', 'result_id', 'commit']

        assert 'ran_on' in hdat.get_unused_keys(mock_keys, distinct_keys)
        assert 'metrics.*' in hdat.get_unused_keys(mock_keys, distinct_keys)

    def test_more_distinct(self, mock_keys):
        mock_keys = ['case_id', 'result_id', 'commit']

        assert not hdat.get_unused_keys(mock_keys, mock_keys)

    def test_non_dict_wildcard(self, mock_keys):
        distinct_keys = ['case_id', 'result_id', 'commit', 'ran_on', 'metrics']

        assert 'metrics.*' in hdat.get_unused_keys(mock_keys, distinct_keys)

    def test_non_wildcard(self):
        mock_keys = ['case_id', 'result_id', 'metrics']
        distinct_keys = ['case_id', 'result_id', 'metrics.mean', 'metrics.std']

        assert 'metrics' in hdat.get_unused_keys(mock_keys, distinct_keys)


class TestGetResults:
    def test_no_data(self, mock_results):
        assert not hdat.get_result_data('undefined_key', mock_results[0])

    def test_matched_data(self, mock_results):
        assert hdat.get_result_data('case_id', mock_results[0]) == '1'

    def test_nested_data(self):
        mock_result = {
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

        assert hdat.get_result_data('metrics.max', mock_result) == '100'
        assert not hdat.get_result_data('metrics.', mock_result)


class TestPrintResult:
    def test_print_default(self, mock_results, capfd):
        hdat.print_results([mock_results[0]], None)
        out, err = capfd.readouterr()
        assert out == 'case_id, ran_on, result_id\n1, 100, r1\n'
        assert 'commit' in err and 'metrics.*' in err

    def test_all_matching_inputs(self, mock_results, capfd):
        hdat.print_results([mock_results[0]], 'suite_id,case_id,result_id,ran_on')
        out, err = capfd.readouterr()
        assert out == 'case_id, ran_on, result_id, suite_id\n1, 100, r1, a\n'
        assert not err
