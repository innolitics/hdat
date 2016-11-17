import os
import json
import copy
import pickle


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

    def select_all(self, *args):
        top_directory = os.path.join(self.root, *args)

        result_filenames = []
        for dirpath, _, filenames in os.walk(top_directory):
            result_filenames.extend([os.path.join(dirpath, p) for p in filenames])

        results = []
        for filename in result_filenames:
            result = self.read_result(filename)
            results.append(result)

        results_sorted = sorted(results, key=lambda r: r['ran_on'])

        return results

    def _strip_context(self, result):
        try:
            del result['context']
        except KeyError:
            pass

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
