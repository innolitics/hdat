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
    if len(resultspec_parts) != 3:
        msg = 'Invalid result spec "{}".  Must point to file or have form "SUITE_ID.CASE_ID.RESULT_ID"'
        raise AbortError(msg.format(resultspec))

    result = archive.select(*resultspec_parts)
    if result is None:
        msg = 'Unable to locate result "{}" in the archive at "{}"'
        raise AbortError(msg.format(resultspec, archive.root))
    else:
        return result
