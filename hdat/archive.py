import os
import pickle
import traceback

from collections import namedtuple
from .util import AbortError


class Archive:
    def __init__(self, directory, suites):
        self.root = os.path.abspath(directory)
        self.suites = suites
        os.makedirs(self.root, exist_ok=True)

    def select(self, suite_id, case_id, result_id):
        """
        Return a single result specified
        """
        result_filename = self._result_filename(suite_id, case_id, result_id)

        if not os.path.isfile(result_filename):
            return None
        else:
            return self.read_result(result_filename)

    def select_recent(self, i, *args):
        """
        Return the most recent result of a specified case.
        *args -- suite and case ID selectors ['a', '1']
        """
        top_directory = os.path.join(self.root, *args)
        if not os.path.isdir(top_directory):
            if args[1] in self.suites[str(args[0])].collect().keys():
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

    def select_recents_suite(self, *args):
        """
        Return the most recent result of each case within a specified suite.
        *args -- suite ID selector ['a']
        """
        top_directory = os.path.join(self.root, *args)
        cases = self.suites[str(*args)].collect().keys()
        if not os.path.isdir(top_directory):
            msg = "Selected suite directory {} does not exist or is not a directory"
            raise AbortError(msg.format(top_directory))
        # catch unused cases within a suite when resultspec is an entire suite
        for case in cases:
            if case not in os.listdir(top_directory):
                msg = 'The case "{}" exists within suite "{}", ' + \
                      'but has no result recorded. ' + \
                      'Please run the case or suite first.'
                raise AbortError(msg.format(case, args[0]))
        for entry in os.listdir(top_directory):
            case_path = os.path.join(top_directory, entry)
            if not entry.startswith('.') and os.path.isdir(case_path) and entry in cases:
                yield self.select_recent(-1, *(args+(entry,)))

    def select_recents_all(self):
        for entry in os.listdir(self.root):
            if not entry.startswith('.') and os.path.isdir(os.path.join(self.root, entry)):
                yield from self.select_recents_suite(entry)

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

    def resolve_resultspecs(self, resultspecs):
        for resultspec in resultspecs:
            results = self.resolve_resultspec(resultspec)
            for result in results:
                yield result

    def resolve_resultspec(self, resultspec):
        if os.path.isfile(resultspec):
            try:
                return [self.read_result(resultspec)]
            except Exception:
                traceback.print_exc()
                msg = 'Unable to read resultspec "{}"'
                raise AbortError(msg.format(resultspec))

        if resultspec == '':
            resultspec_parts = []
        else:
            resultspec_parts = resultspec.split('/')

        # Pull most recent result from all cases available: resultspec == ''
        pick_recents_all_suites = len(resultspec_parts) == 0
        # Pull most recent result from all cases in a suite: resultspec == <suite_id>
        pick_recents_one_suite = len(resultspec_parts) == 1
        # Pull most recent result from a case: resultspec == <suite_id>/<case_id>
        pick_recent = len(resultspec_parts) == 2
        # Pull (n+1)th most recent reuslt from a case: resultspec == <suite_id>/<case_id>/~<n>
        pick_by_index = len(resultspec_parts) == 3 and resultspec_parts[2].startswith('~')
        # Pull specific result: resultspec == <suite_id>/<case_id>/<result_id>
        pick_by_result_id = len(resultspec_parts) == 3 and not pick_by_index

        if pick_recent or pick_by_index:
            print(self.suites)
            if resultspec_parts[1] not in self.suites[resultspec_parts[0]].collect().keys():
                msg = 'Unable to locate "{}"; the case "{}" does not exist within suite "{}"'
                raise AbortError(msg.format(resultspec, resultspec_parts[1], resultspec_parts[0]))
            if pick_recent:
                i = -1
            else:
                try:
                    i = -1 - int(resultspec_parts[2][1:])
                except ValueError:
                    msg = 'Invalid resultspec "{}"; the third part must be a valid result_id' + \
                        'or a tilde followed by an integer, but not "{}"'
                    raise AbortError(msg.format(resultspec, resultspec_parts[2][1]))
            try:
                result = self.select_recent(i, *resultspec_parts[:2])
                return [result]
            except IndexError:
                msg = 'Unable to locate any results matching "{}", there are more than {} results present.'
                raise AbortError(msg.format(resultspec, i))
        elif pick_by_result_id:
            result = self.select(*resultspec_parts)
            if result is None:
                msg = 'Unable to locate result "{}" in the archive at "{}"'
                raise AbortError(msg.format(resultspec, self.root))
            else:
                return [result]
        elif pick_recents_all_suites:
            return self.select_recents_all()
        elif pick_recents_one_suite:
            return self.select_recents_suite(resultspec_parts[0])
        else:
            msg = 'Invalid result spec "{}". ' + \
                  'Resultspecs must point to a result file, ' + \
                  'have the fully qualified form "SUITEID/CASEID/RESULTID", ' + \
                  'or if it is partially qualified, such as "SUITEID/CASEID", ' + \
                  'it will select the most recent result that matches.'
            raise AbortError(msg.format(resultspec))


def print_resultspec(result):
    try:
        suite_id = result['suite_id']
        case_id = result['case_id']
        result_id = result['result_id']
        return '{}/{}/{}'.format(suite_id, case_id, result_id)
    except KeyError:
        return 'Invalid result "{}"'.format(repr(result))
