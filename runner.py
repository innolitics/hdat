import sys
import os
import argparse
import datetime
import pydoc

from hdatt.util import print_error, AbortError


def run_cases(suites, golden_store, archive, git_info, cases):
    '''
    Run a list of cases, store results in the archive, and verify against
    results in the golden_store.

    Cases are specified by a list of tuples of the form `(suite_id, case_id)`.

    This function assumes that all cases are valid.
    '''
    num_failures = 0
    for suite_id, case_id in cases:
        suite = suites[suite_id]
        try:
            passed = run_case(suite, golden_store, archive, git_info, case_id)
        except Exception as e:
            msg = 'Error while running "{}.{}": {}'
            print_error(msg.format(suite_id, case_id, e))
            passed = False

        if passed:
            print('PASS "{}.{}"'.format(suite_id, case_id))
        else:
            print('FAIL "{}.{}"'.format(suite_id, case_id))
            num_failures += 1

    if num_failures > 0:
        raise AbortError('{} of {} tests failed'.format(num_failures, len(cases)))


def run_case(suite, golden_store, archive, git_info, case_id):
    case_input = suite.collect()[case_id]
    run_result = suite.run(case_input)
    validate_result(run_result)
    metrics, context = run_result

    golden_result = golden_store.select_golden(suite.id(), case_id)

    if golden_result is None:
        passed, comments = False, 'No golden result present'
    else:
        passed, comments = suite.verify(golden_result['metrics'], metrics)

    result = build_result(suite, git_info, case_id, metrics, context, passed)
    archive.insert(result)
    return passed


def validate_result(run_result):
    if type(run_result) != tuple and len(run_result) == 2:
        msg = 'Test suites must return a tuple of the form (metrics, context).  Got "{}".'
        raise ValueError(msg.format(repr(run_result)))


def build_result(suite, git_info, case_id, metrics, context, passed):
    run_datetime = datetime.datetime.utcnow()
    result = {
        'suite_id': suite.id(),
        'case_id': case_id,
        'commit': git_info['commit'],
        'repo_dirty': git_info['dirty'],
        'ran_on': run_datetime.timestamp(),
        'metrics': metrics,
        'context': context,
        'passed': passed,
    }

    result['result_id'] = suite.build_result_id(result)
    return result


