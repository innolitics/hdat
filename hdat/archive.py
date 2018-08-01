import os
import pickle
from collections.__init__ import namedtuple

from hdat.util import AbortError


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
                raise AbortError(msg.format(args[1], args[0]))
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
                raise AbortError(msg.format(case, args[0]))
        for entry in os.listdir(top_directory):
            if (not entry.startswith('.') and
                    os.path.isdir(os.path.join(top_directory, entry)) and
                    entry in suites[str(*args)].collect().keys()):
                yield self.select_recent(suites, -1, *(args+(entry,)))

    def select_recents_all(self, suites):
        for entry in os.listdir(self.root):
            if not entry.startswith('.') and os.path.isdir(os.path.join(self.root, entry)):
                yield from self.select_recents_suite(suites, entry)

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