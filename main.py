import argparse

from hdatt.resultspec import resolve_resultspec
from hdatt.casespec import resolve_casespecs
from hdatt.runner import run_cases


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='hdatt')
    subparsers = parser.add_subparsers(dest='command', metavar='<command>')

    run_help = 'run cases, store results in archive, compare against goldens'
    run_parser = subparsers.add_parser('run', help=run_help)
    run_parser.add_argument('casespecs', nargs='*', default=[''], metavar='<case>')

    show_help = 'visualize a single result'
    show_parser = subparsers.add_parser('show', help=show_help)
    show_result_help = 'result specifier to show'
    show_parser.add_argument('resultspec', nargs=1, metavar='<result>', help=show_result_help)

    diff_help = 'compare two results'
    diff_parser = subparsers.add_parser('diff', help=diff_help)
    diff_golden_help = 'result to compare to (defaults to current golden)'
    diff_parser.add_argument('goldenspec', nargs='?', default=None, metavar='<golden>', help=diff_golden_help)
    diff_result_help = 'result being compared'
    diff_parser.add_argument('resultspec', nargs=1, metavar='<result>', help=diff_result_help)

    verify_help = 'move result metrics from archive to the golden store'
    verify_parser = subparsers.add_parser('verify', help=verify_help)
    verify_result_help = 'result being stripped and moved into the golden store'
    verify_parser.add_argument('resultspec', metavar='<result>', help=verify_result_help)

    return parser.parse_args(arguments)


def main(arguments, suites, golden_store, archive, git_info):
    args = parse_arguments(arguments)

    if args.command is None:
        parse_arguments(['-h'])

    if args.command == 'run':
        cases = resolve_casespecs(suites, args.casespecs)
        run_cases(suites, golden_store, archive, git_info, cases)
    elif args.command == 'show':
        result = select_result(archive, golden_store, args.resultspec)
        show_result(suites, result)
    elif args.command == 'diff':
        golden_result = select_result(archive, golden_store, args.goldenspec)
        result = select_result(archive, golden_store, args.resultspec)
        diff_result(suites, golden_result, result)
    elif args.command == 'verify':
        result = resolve_resultspec(archive, args.resultspec)
        golden_store.insert(result)
