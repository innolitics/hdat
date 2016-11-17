import os
import traceback

from hdatt.util import AbortError


def resolve_resultspec(archive, resultspec):
    if os.path.isfile(resultspec):
        try:
            return archive.read_result(resultspec)
        except Exception as e:
            traceback.print_exc()
            msg = 'Unable to read resultspec "{}"'
            raise AbortError(msg.format(resultspec))

        
    if resultspec == '':
        resultspec_parts = []
    else:
        resultspec_parts = resultspec.split('/')

    if len(resultspec_parts) < 3:
        # TODO: make this faster in the event there are many results
        results = archive.select_all(*resultspec_parts)
        if len(results) == 0:
            msg = 'Unable to locate any results matching "{}" in the archive at "{}"'
            raise AbortError(msg.format(resultspec, archive.root))
        else:
            return results[-1]

    elif len(resultspec_parts) == 3:
        result = archive.select(*resultspec_parts)
        if result is None:
            msg = 'Unable to locate result "{}" in the archive at "{}"'
            raise AbortError(msg.format(resultspec, archive.root))
        else:
            return result

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
