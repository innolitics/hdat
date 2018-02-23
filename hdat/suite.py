import importlib
import sys
import inspect
import os

from .util import print_error, AbortError


class Suite:
    '''
    Base class for a suite of algorithm test cases.

    Is responsible for collecting, running, checking, and visualizing the
    results of running the algorithm against its test cases.
    '''
    def collect(self):
        '''
        Collect all of the cases for this suite, and return them as a dict-like
        mapping where the keys are the "case ids" and the values are the "case
        data"---whatever is needed to run the case.
        '''
        raise NotImplementedError()

    def check(self, golden_metrics, metrics):
        '''
        Given two result comparable outputs, check if the second result passes based on
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

    @property
    def id(self):
        return type(self).__name__


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

        suite_id = suite.id
        if suite_id in mapping:
            raise AbortError('Duplicate suite id "{}"'.format(suite_id))
        elif '/' in suite_id:
            raise AbortError('Invalid suite id "{}", no "/" allowed in suite ids'.format(suite_id))
        else:
            mapping[suite_id] = suite
    return mapping


def _collect_suite_classes(directory):
    hdat_module_suffix = '_hdat.py'
    hdat_suite_class = Suite

    suite_classes = []
    for root, dirs, files in os.walk(directory, topdown=True):
        # prevent os.walk from going into hidden dirs
        dirs[:] = [subdir for subdir in dirs if not subdir.startswith('.')]
        for filename in files:
            if filename.endswith(hdat_module_suffix):
                module_name = filename.strip(".py")

                module_path = (os.path.relpath(root, start=directory))
                if module_path == '.':
                    module_spec = module_name
                else:
                    module_spec = os.path.join(module_path, '').replace(os.path.sep, '.') + module_name

                importlib.import_module(module_spec)
                classes = inspect.getmembers(sys.modules[module_spec], predicate=inspect.isclass)
                for name, value in classes:
                    if hdat_suite_class in inspect.getmro(value) and hdat_suite_class != value:
                        suite_classes.append(value)
    return suite_classes


def ignore_key_errors(decoratee):
    def decorated(*args, **kwargs):
        try:
            return decoratee(*args, **kwargs)
        except KeyError:
            pass
    return decorated


class MetricsChecker:
    '''
    Helper class for comparing metrics of new results vs golden results in suite.check()
    '''
    def __init__(self, old, new):
        self._old = old
        self._new = new
        self._match = True
        self._msgs = []
        missing_metrics = set(old.keys()).difference(set(new.keys()))
        new_metrics = set(new.keys()).difference(set(old.keys()))
        if missing_metrics:
            msg = 'Metric(s) in golden result {} were missing from the new run'
            self._msgs.append(msg.format(missing_metrics))
            self._match = False
        if new_metrics:
            msg = 'New metric(s) {} added to hdat test suite'
            self._msgs.append(msg.format(new_metrics))

    def _isclose(self, a, b, rel_tol=1e-09, abs_tol=0.0):
        '''Fills in for math.isclose in 3.4'''
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

    @ignore_key_errors
    def close(self, metric, **kwargs):
        if not self._isclose(self._old[metric], self._new[metric], **kwargs):
            self._match = False
            msg = 'Metric {} value {} was not close to golden value {} within {}'
            self._msgs.append(msg.format(metric, self._new[metric], self._old[metric], kwargs))

    @ignore_key_errors
    def exact(self, metric):
        if self._old[metric] != self._new[metric]:
            self._match = False
            msg = 'Metric {} value {} did not match golden value {}'
            self._msgs.append(msg.format(metric, self._new[metric], self._old[metric]))

    @ignore_key_errors
    def custom(self, metric, func=None):
        result, msg = func(self._old[metric], self._new[metric])
        if not result:
            self._match = False
            self._msgs.append(msg)

    @ignore_key_errors
    def can_increase(self, metric, abs_tol=0.0):
        if (self._new[metric] + abs_tol < self._old[metric] and
                not self._isclose(self._new[metric], self._old[metric])):
            self._match = False
            msg = 'Metric {} value {} decreased over golden value {} more than {}'
            self._msgs.append(msg.format(metric, self._new[metric], self._old[metric], abs_tol))

    @ignore_key_errors
    def can_decrease(self, metric, abs_tol=0.0):
        if (self._new[metric] - abs_tol > self._old[metric] and
                not self._isclose(self._new[metric], self._old[metric])):
            self._match = False
            msg = 'Metric {} value {} increased over golden value {} more than {}'
            self._msgs.append(msg.format(metric, self._new[metric], self._old[metric], abs_tol))

    def msgs(self):
        return self._msgs

    def match(self):
        return self._match

    def result(self):
        return self._match, self._msgs
