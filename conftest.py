import tempfile

import pytest

from hdatt.store import GoldenStore, Archive
from hdatt.suite import Suite


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


class BasicSuiteA(Suite):
    def id(self):
        return 'a'

    def collect(self):
        return {
            '1': 10,
            '2': 20,
        }

    def verify(self, old, new):
        return old == new, 'Looks good!'

    def run(self, case_input):
        return case_input, {}


class BasicSuiteB(Suite):
    def id(cls):
        return 'b'

    def collect(self):
        return {
            '3': 30,
        }

    def verify(self, old, new):
        return old == new, 'Looks good!'

    def run(self, case_input):
        return case_input, {}


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
