import os
import traceback

from .util import AbortError


def resolve_resultspecs(archive, resultspec):
    if os.path.isfile(resultspec):
        try:
            return [archive.read_result(resultspec)]
        except Exception:
            traceback.print_exc()
            msg = 'Unable to read resultspec "{}"'
            raise AbortError(msg.format(resultspec))

    if resultspec == '':
        resultspec_parts = []
    else:
        resultspec_parts = resultspec.split('/')

    pick_recents_all_suites = len(resultspec_parts) == 0
    pick_recents_one_suite = len(resultspec_parts) == 1
    pick_recent = len(resultspec_parts) == 2
    pick_by_index = len(resultspec_parts) == 3 and resultspec_parts[2].startswith('~')
    pick_by_result_id = len(resultspec_parts) == 3 and not pick_by_index

    if pick_recent or pick_by_index:
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
            result = archive.select_recent(i, *resultspec_parts[:2])
            return [result]
        except IndexError:
            msg = 'Unable to locate any results matching "{}", there are more than {} results present.'
            raise AbortError(msg.format(resultspec, i))
    elif pick_by_result_id:
        result = archive.select(*resultspec_parts)
        if result is None:
            msg = 'Unable to locate result "{}" in the archive at "{}"'
            raise AbortError(msg.format(resultspec, archive.root))
        else:
            return [result]
    elif pick_recents_all_suites:
        return archive.select_recents_all()
    elif pick_recents_one_suite:
        return archive.select_recents_suite(resultspec_parts[0])
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
