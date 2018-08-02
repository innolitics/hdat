import numpy as np
import pytest


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
