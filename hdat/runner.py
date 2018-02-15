import datetime
import traceback

from .casespec import print_casespec


def run_cases(suites, golden_store, archive, git_info, cases):
    '''
    Run a list of cases, store results in the archive, and check against
    results in the golden_store.

    Cases are specified by a list of tuples of the form `(suite_id, case_id)`.

    This function assumes that all cases are valid.
    '''
    cases_status = {
        'pass': 0,
        'fail': 0,
        'error': 0,
        'unknown': 0,
    }
    for suite_id, case_id in cases:
        suite = suites[suite_id]
        casespec = print_casespec(suite_id, case_id)
        print('STARTING CASE "{}"'.format(casespec))
        try:
            status, comments = run_case(suite, golden_store, archive, git_info, case_id)
        except Exception:
            comments = 'Error "{}"'.format(casespec)
            status = 'error'
            traceback.print_exc()

        cases_status[status] += 1
        print('Case "{}" status: {}\n{}\n'.format(casespec, status.upper(), comments))

    return cases_status


def run_case(suite, golden_store, archive, git_info, case_id):
    case_input = suite.collect()[case_id]
    run_result = suite.run(case_input)
    validate_result(run_result)
    metrics, context = run_result

    golden_result = golden_store.select_golden(suite.id, case_id)

    if golden_result is None:
        status, comments = 'unknown', 'No golden result present'
    else:
        passed, comments = suite.check(golden_result['metrics'], metrics)
        status = 'pass' if passed else 'fail'

    result = build_result(suite, git_info, case_id, case_input, metrics, context, status)
    archive.insert(result)
    return status, comments


def validate_result(run_result):
    if type(run_result) != tuple and len(run_result) == 2:
        msg = 'Test suites must return a tuple of the form (metrics, context).  Got "{}".'
        raise ValueError(msg.format(repr(run_result)))


def build_result_id(result):
        return '{}_{}'.format(result['ran_on'], result['commit'])


def build_result(suite, git_info, case_id, case_input, metrics, context, status):
    run_datetime = datetime.datetime.utcnow()
    result = {
        'suite_id': suite.id,
        'case_id': case_id,
        'case_input': case_input,
        'commit': git_info['commit'],
        'repo_dirty': git_info['dirty'],
        'ran_on': run_datetime.timestamp(),
        'metrics': metrics,
        'context': context,
        'status': status,
    }

    result['result_id'] = build_result_id(result)
    return result
