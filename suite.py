import datetime

from hdatt.util import print_error, find_here_or_in_parents, AbortError


class Suite:
    '''
    Base class for a suite of algorithm test cases.

    Is responsible for collecting, running, verifying, and visualizing the
    results of running the algorithm against its test cases.
    '''
    def cases(self):
        '''
        Collect all of the cases for this suite, and return them as a dict-like
        mapping where the keys are the "case ids" and the values are the "case
        data"---whatever is needed to run the case.
        '''
        raise NotImplementedError()

    def verify(self, golden_metrics, metrics):
        '''
        Given two result comparable outputs, verify if the second result passes based on
        the first result.  Should return a tuple with a boolean and a string
        with any comments.
        '''
        raise NotImplementedError()

    def run(self, case_input):
        '''
        Run the algorithm against a particular set of "case data".  Should
        return a two-tuple.  The first value of this tuple should contain a
        low-dimensional, easily comparable distilled version of the output.
        The second value can contain any context needed to visualize and
        interpret the result.  The context can be much larger and can contain
        the full result of running the algorithm.
        '''
        raise NotImplementedError()
    
    def show(self, result):
        raise NotImplementedError()

    def diff(self, golden_result, result):
        raise NotImplementedError()

    def id(self):
        return type(self).__name__

    def build_result_id(self, result_without_id):
        seconds_timestamp = int(result_without_id['ran_on'])
        return '{}-{}'.format(seconds_timestamp, result_without_id['commit'])


def collect_suites(directory):
    suite_classes = _collect_suite_classes(directory)
    mapping = {}
    for suite_class in suite_classes:
        try:
            suite = suite_class()
        except Exception as e:
            print_error(e)
            suite_class_name = suite_class.__name__
            msg = 'Error while instatiating suite "{}"'
            raise AbortError(msg.format(suite_class_name))

        suite_id = suite.id()
        if suite_id in mapping:
            raise AbortError('Duplicate suite id "{}"'.format(suite_id))
        elif '.' in suite_id:
            raise AbortError('Invalid suite id "{}", no "." allowed'.format(suite_id))
        else:
            mapping[suite_id] = suite
    return mapping


def _collect_suite_classes(directory):
    suites_filename = find_here_or_in_parents(directory, '.hdattsuites')
    if suites_filename is None:
        raise AbortError('Unable to locate a ".hdattsuites" file')

    suite_classes = []
    with open(suites_filename, 'r') as suites_file:
        for line in suites_file:
            class_location = line.strip()
            try:
                test_suite_class = pydoc.locate(class_location)
            except pydoc.ErrorDuringImport as e:
                print_error(e)
                test_suite_class = None

            if test_suite_class is None:
                msg = 'Unable to import test suite "{}"'
                raise AbortError(msg.format(class_location))
            else:
                suite_classes.append(test_suite_class)

    return suite_classes
