import os
import json
import copy
import pickle
from collections import namedtuple

from .util import AbortError, UnusedCaseError


class Archive:
    def __init__(self, directory):
        self.root = os.path.abspath(directory)
        os.makedirs(self.root, exist_ok=True)

    def select(self, suite_id, case_id, result_id):
        result_filename = self._result_filename(suite_id, case_id, result_id)

        if not os.path.isfile(result_filename):
            return None
        else:
            return self.read_result(result_filename)

    def select_recent(self, suites, i, *args):
        top_directory = os.path.join(self.root, *args)
        if not os.path.isdir(top_directory):
            if args[1] in suites[str(args[0])].collect().keys():
                msg = 'The case "{}" exists within suite "{}", ' + \
                      'but has no result recorded. ' + \
                      'Please run the case or suite first.'
                raise UnusedCaseError(msg.format(args[1], args[0]))
            msg = "Selected case directory {} does not exist or is not a directory"
            raise AbortError(msg.format(top_directory))

        results = []
        ResultDesc = namedtuple('ResultDesc', ('id', 'ran_on'))
        id_to_full_result = dict()

        for entry in os.listdir(top_directory):
            if not entry.startswith('.') and os.path.isfile(os.path.join(top_directory, entry)):
                # check for ran_on timestamp as part of <timestamp>_<commit_id> result ID format
                try:
                    ran_on = float(entry.split('_')[0])
                    results.append(ResultDesc(entry, ran_on))
                except ValueError:
                    result = self.read_result(os.path.join(top_directory, entry))
                    ran_on = result['ran_on']
                    id_to_full_result[entry] = result
                    results.append(ResultDesc(entry, ran_on))

        results_sorted = sorted(results, key=lambda r: r.ran_on)
        recent_id = results_sorted[i].id

        if recent_id in id_to_full_result:
            return id_to_full_result[recent_id]
        else:
            return self.read_result(os.path.join(top_directory, recent_id))

    def select_recents_suite(self, suites, *args):
        top_directory = os.path.join(self.root, *args)
        if not os.path.isdir(top_directory):
            msg = "Selected suite directory {} does not exist or is not a directory"
            raise AbortError(msg.format(top_directory))
        # catch unused cases within a suite when resultspec is an entire suite
        for case in suites[str(args[0])].collect().keys():
            if case not in os.listdir(top_directory):
                msg = 'The case "{}" exists within suite "{}", ' + \
                      'but has no result recorded. ' + \
                      'Please run the case or suite first.'
                raise UnusedCaseError(msg.format(case, args[0]))
        for entry in os.listdir(top_directory):
            if (not entry.startswith('.') and
                    os.path.isdir(os.path.join(top_directory, entry)) and
                    entry in suites[str(*args)].collect().keys()):
                try:
                    yield self.select_recent(suites, -1, *(args+(entry,)))
                except UnusedCaseError as e:
                    raise UnusedCaseError(str(e))
# hard to handle this one: want to raise an error but return the rest
# if we move this past the `for entry in` loop, it works for a single unused case but not if there are multiple
# using a boolean to tell if there are any errors and printing as they come

    def select_recents_all(self, suites):
        for entry in os.listdir(self.root):
            if not entry.startswith('.') and os.path.isdir(os.path.join(self.root, entry)):
                try:
                    yield from self.select_recents_suite(suites, entry)
                except UnusedCaseError as e:
                    raise UnusedCaseError(str(e))

    def insert(self, result):
        suite_id = result['suite_id']
        case_id = result['case_id']
        result_id = result['result_id']

        case_directory = os.path.join(self.root, suite_id, case_id)
        os.makedirs(case_directory, exist_ok=True)

        result_filename = self._result_filename(suite_id, case_id, result_id)

        if os.path.isfile(result_filename):
            raise IOError('Result file exists "{}"'.format(result_filename))

        with open(result_filename, 'wb') as result_file:
            pickle.dump(result, result_file)

    def read_result(self, filename):
        with open(filename, 'rb') as result_file:
            return pickle.load(result_file)

    def _result_filename(self, suite_id, case_id, result_id):
        return os.path.join(self.root, suite_id, case_id, result_id + '.pkl')


class GoldenStore:
    def __init__(self, directory):
        self.root = os.path.abspath(directory)
        os.makedirs(self.root, exist_ok=True)

    def select_golden(self, suite_id, case_id):
        golden_filename = self._golden_filename(suite_id, case_id)
        if not os.path.isfile(golden_filename):
            return None
        with open(golden_filename, 'r') as golden_file:
            return json.load(golden_file)

    def insert(self, result):
        result = self._strip_result(result)

        suite_id = result['suite_id']
        case_id = result['case_id']

        suite_directory = os.path.join(self.root, suite_id)
        os.makedirs(suite_directory, exist_ok=True)

        golden_filename = self._golden_filename(suite_id, case_id)
        with open(golden_filename, 'w') as golden_file:
            json.dump(result, golden_file, sort_keys=True, indent=4)

    def _golden_filename(self, suite_id, case_id):
        return os.path.join(self.root, suite_id, case_id + '.json')

    def _strip_result(self, result):
        # we don't do a deep copy until we have deleted the potentially large
        # "context" key
        shallow_copied_result = copy.copy(result)
        try:
            del shallow_copied_result['context']
            del shallow_copied_result['case_input']
        except KeyError:
            pass
        deeply_copied_result = copy.deepcopy(shallow_copied_result)
        return deeply_copied_result
