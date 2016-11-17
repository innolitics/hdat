import os

from hdatt.util import AbortError


def resolve_resultspec(archive, resultspec):
    if os.path.isfile(resultspec):
        try:
            return archive.read_result(resultspec)
        except Exception as e:
            msg = 'Unable to read resultspec "{}": {}'
            raise AbortError(msg.format(resultspec, e))

    resultspec_parts = resultspec.split('.')

    if len(resultspec_parts) == 2:
        results = archive.select_all(*resultspec_parts)
        if len(results) == 0:
            msg = 'Unable to locate any results for case "{}" in the archive at "{}"'
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
              'have the fully qualified form "SUITEID.CASEID.RESULTID", ' + \
              'or have the form "SUITEID.CASEID" in which case the ' + \
              'most resent result for that case is used.'
        raise AbortError(msg.format(resultspec))
