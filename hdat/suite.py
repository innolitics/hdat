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
