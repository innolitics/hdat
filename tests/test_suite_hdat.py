from hdat.suite import Suite
from collections import OrderedDict
from hdat.resultspec import print_resultspec


class BaseSuite(Suite):
    def check(self, old, new):
        return old == new, 'Looks good!'

    def run(self, case_input):
        return case_input, {}

    def collect(self):
        return OrderedDict()

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
