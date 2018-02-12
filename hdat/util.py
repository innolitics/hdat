import os
import sys


class AbortError(Exception):
    pass


def print_error(message):
    print(message, file=sys.stderr)


def find_here_or_in_parents(start_directory, entryname):
    current_directory = os.path.abspath(start_directory)

    while current_directory != '/':
        test_entryname = os.path.join(current_directory, entryname)
        if os.path.exists(test_entryname):
            return test_entryname
        else:
            current_directory = os.path.dirname(current_directory)

    return None


def repository_root(start_directory):
    git_directory = find_here_or_in_parents(start_directory, '.git')
    if git_directory is None:
        raise ValueError('Not in a git repository')
    else:
        return os.path.dirname(git_directory)


def remove_duplicates(list_w_duplicates):
    list_wout_duplicates = []
    seen = set()
    for i in list_w_duplicates:
        if i in seen:
            continue
        else:
            seen.add(i)
            list_wout_duplicates.append(i)
    return list_wout_duplicates
