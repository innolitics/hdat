import os
import json
import copy


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
