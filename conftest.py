import tempfile
from collections import OrderedDict

import pytest

from .store import GoldenStore, Archive
from .suite import Suite
from .resultspec import print_resultspec


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
    def verify(self, old, new):
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
