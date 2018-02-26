#!/usr/bin/env python3
import sys
import os

from hdat.hdat_cli import hdat_cli
from hdat.suite import collect_suites
from hdat.source_control import git_info_from_directory
from hdat.util import repository_root, print_error, AbortError
from hdat.store import Archive, GoldenStore


def main():
    cwd = os.getcwd()
    sys.path.append(cwd)

    try:
        git_info = git_info_from_directory(cwd)
        repo_directory = repository_root(cwd)

        if 'HDAT_ARCHIVE' in os.environ:
            archive_location = os.environ['HDAT_ARCHIVE']
        else:
            archive_location = os.path.join(repo_directory, '.hdatarchive')
        archive = Archive(archive_location)

        golden_store_location = os.path.join(repo_directory, 'golden_results')
        golden_store = GoldenStore(golden_store_location)

        suites = collect_suites(cwd)

        hdat_cli(sys.argv[1:], suites, golden_store, archive, git_info)

        sys.exit(0)

    except AbortError as e:
        print_error(e)

        sys.exit(1)


if __name__ == '__main__':
    main()
