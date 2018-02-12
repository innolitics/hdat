import os

import numpy as np
import pytest


class TestGoldenStore:
    def test_select_missing(self, tmp_golden_store):
        assert tmp_golden_store.select_golden('sid', 'cid') == None

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


class TestArchive:
    def test_insert_then_select(self, tmp_archive):
        result = {
            'suite_id': 'sid',
            'case_id': 'cid',
            'result_id': 'rid',
            'context': {'a': np.random.rand(2, 2)},
        }
        tmp_archive.insert(result)
        data = tmp_archive.select('sid', 'cid', 'rid')
        assert result['suite_id'] == data['suite_id']
        assert np.alltrue(result['context']['a'] == data['context']['a'])

    def test_overwrite_fails(self, tmp_archive):
        result = {
            'suite_id': 'sid',
            'case_id': 'cid',
            'result_id': 'rid',
            'context': 'a',
        }
        tmp_archive.insert(result)
        result['context'] = 'b'
        with pytest.raises(IOError):
            tmp_archive.insert(result)
