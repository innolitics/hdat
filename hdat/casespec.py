from .util import AbortError, remove_duplicates


def resolve_casespecs(suites, casespecs):
    cases = []
    for spec in casespecs:
        cases.extend(resolve_casespec(suites, spec))
    return remove_duplicates(cases)


def resolve_casespec(suites, casespec):
    cases = []
    spec_parts = casespec.split('/')
    if casespec == '':
        for suite_id, suite in suites.items():
            for case_id in suite.collect():
                cases.append((suite_id, case_id))
    elif len(spec_parts) == 1:
        suite_id = spec_parts[0]
        suite = select_suite(suites, suite_id)
        for case_id in suite.collect():
            cases.append((suite_id, case_id))
    elif len(spec_parts) == 2:
        suite_id, case_id = spec_parts
        suite = select_suite(suites, suite_id)
        select_case(suite, case_id)
        cases.append((suite_id, case_id))
    else:
        raise AbortError('Invalid case specifier "{}"'.format(casespec))
    return cases


def select_suite(suites, suite_id):
    if suite_id not in suites:
        all_suites = '\n- '.join(suites.keys())
        msg = 'Unknown suite id "{}". Available suites:\n- {}'
        raise AbortError(msg.format(suite_id, all_suites))
    else:
        return suites[suite_id]


def select_case(suite, case_id):
    case_map = suite.collect()
    if case_id not in case_map:
        all_cases = '\n- '.join(case_map.keys())
        msg = 'Unknown case id "{}". Available cases:\n- {}'
        raise AbortError(msg.format(case_id, all_cases))
    else:
        return case_map[case_id]


def print_casespec(suite_id, case_id):
    return '{}/{}'.format(suite_id, case_id)
