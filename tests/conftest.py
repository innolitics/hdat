import tempfile
from collections import OrderedDict

import pytest

from hdat.store import GoldenStore, Archive
from hdat.suite import Suite
from hdat.resultspec import print_resultspec


@pytest.fixture
def tmp_golden_store():
    tmp_directory = tempfile.TemporaryDirectory()
    yield GoldenStore(tmp_directory.name)
    tmp_directory.cleanup()


@pytest.fixture
def tmp_archive():
    tmp_directory = tempfile.TemporaryDirectory()
    yield Archive(tmp_directory.name)
    tmp_directory.cleanup()


class BaseSuite(Suite):
    def check(self, old, new):
        return old == new, 'Looks good!'

    def run(self, case_input):
        return case_input, {}

    def show(self, result):
        raise NotImplementedError('showing "{}"'.format(
            print_resultspec(result)
        ))

    def diff(self, golden_result, result):
        raise NotImplementedError('diffing "{}" and "{}"'.format(
            print_resultspec(golden_result),
            print_resultspec(result)
        ))


class BasicSuiteA(BaseSuite):
    id = 'a'

    def collect(self):
        return OrderedDict([
            ('1', 10),
            ('2', 20),
        ])


class BasicSuiteB(BaseSuite):
    id = 'b'

    def collect(self):
        return {
            '3': 30,
        }


@pytest.fixture
def basic_suite_a():
    return BasicSuiteA


@pytest.fixture
def basic_suite_b():
    return BasicSuiteB


@pytest.fixture
def mock_git_info():
    return {'commit': 'commit', 'dirty': False}


@pytest.fixture
def mock_suites(basic_suite_a, basic_suite_b):
    return {
        'a': basic_suite_a(),
        'b': basic_suite_b(),
    }


@pytest.fixture
def mock_results():
    return [
        {
            'suite_id': 'a',
            'case_id': '1',
            'result_id': 'r1',
            'ran_on': 100,
        },
        {
            'suite_id': 'a',
            'case_id': '1',
            'result_id': '101_r2',
            'ran_on': 101,
        },
        {
            'suite_id': 'a',
            'case_id': '2',
            'result_id': '103_r3',
            'ran_on': 103,
        },
        {
            'suite_id': 'b',
            'case_id': '1',
            'result_id': '103_r4',
            'ran_on': 104,
        },
    ]


@pytest.fixture
def archive(tmp_archive, mock_results):
    for result in mock_results:
        tmp_archive.insert(result)
    return tmp_archive
