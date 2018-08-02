class TestGoldenStore:
    def test_select_missing(self, tmp_golden_store):
        assert tmp_golden_store.select_golden('sid', 'cid') is None

    def test_insert_then_select(self, tmp_golden_store):
        result = {
            'suite_id': 'sid',
            'case_id': 'cid',
            'result_id': 'rid',
            'context': 'deleteme',
        }
        tmp_golden_store.insert(result)
        assert tmp_golden_store.select_golden('sid', 'cid') == {
            'suite_id': 'sid',
            'case_id': 'cid',
            'result_id': 'rid',
        }

    def test_insert_then_overwrite(self, tmp_golden_store):
        result = {
            'suite_id': 'sid',
            'case_id': 'cid',
            'result_id': 'rid',
            'context': 'deleteme',
        }
        tmp_golden_store.insert(result)
        result['result_id'] = 'new_rid'
        tmp_golden_store.insert(result)
        assert tmp_golden_store.select_golden('sid', 'cid') == {
            'suite_id': 'sid',
            'case_id': 'cid',
            'result_id': 'new_rid',
        }
