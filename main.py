import argparse
import traceback
from collections import ChainMap, OrderedDict

from .resultspec import resolve_resultspec, print_resultspec
from .casespec import resolve_casespecs, select_suite
from .runner import run_cases
from .util import AbortError


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='hdatt')
    subparsers = parser.add_subparsers(dest='command', metavar='<command>')

    run_help = 'run cases, store results in archive, compare against goldens'
    run_parser = subparsers.add_parser('run', help=run_help)
    run_parser.add_argument('casespecs', nargs='*', default=[''], metavar='<case>')
    run_parser.add_argument('--collect-only', default=False, action='store_true')

    show_help = 'visualize a single result'
    show_parser = subparsers.add_parser('show', help=show_help)
    show_result_help = 'result specifier to show'
    show_parser.add_argument('resultspec', nargs="?", default='', metavar='<result>', help=show_result_help)

    diff_help = 'compare two results'
    diff_parser = subparsers.add_parser('diff', help=diff_help)
    diff_golden_help = 'result to compare to (defaults to current golden for the case)'
    diff_parser.add_argument('goldenspec', nargs='?', default=None, metavar='<golden>', help=diff_golden_help)
    diff_result_help = 'result being compared'
    diff_parser.add_argument('resultspec', nargs=1, metavar='<result>', help=diff_result_help)

    verify_help = 'move result metrics from archive to the golden store'
    verify_parser = subparsers.add_parser('verify', help=verify_help)
    verify_result_help = 'results to be stripped and moved into the golden store'
    verify_parser.add_argument('resultspec', nargs='?', default='', metavar='<result>', help=verify_result_help)

    report_help = 'Print a report from the most recent results for a given suite.'
    report_parser = subparsers.add_parser('report', help=report_help)
    report_help = 'suite to generate and print out a report for.'
    report_parser.add_argument('suitespec', default='', metavar='<suite>', help=report_help)

    return parser.parse_args(arguments)


def main(arguments, suites, golden_store, archive, git_info):
    args = parse_arguments(arguments)

    if args.command is None:
        parse_arguments(['-h'])

    if args.command == 'run' and args.collect_only:
        cases = resolve_casespecs(suites, args.casespecs)
        print("\n".join(['{}/{}'.format(s, c) for s, c in cases]))
    elif args.command == 'run':
        cases = resolve_casespecs(suites, args.casespecs)
        run_cases(suites, golden_store, archive, git_info, cases)
    elif args.command == 'show':
        result = resolve_resultspec(archive, args.resultspec)
        show_result(suites, result)
    elif args.command == 'diff':
        golden_result = resolve_resultspec(archive, args.goldenspec)
        result = resolve_resultspec(archive, args.resultspec)
        suite.diff_results(suites, golden_result, result)
    elif args.command == 'verify':
        result = resolve_resultspec(archive, args.resultspec)
        golden_store.insert(result)
    elif args.command == 'report':
        suite = select_suite(suites, args.suitespec)
        result_specs = ['{}/{}'.format(args.suitespec, case_id) for case_id in suite.collect()]
        results = [resolve_resultspec(archive, result_spec) for result_spec in result_specs]
        table = []
        for result in results:
            row = OrderedDict({'case id': result['case_id']})
            row.update(result['metrics'])
            table.append(row)

        # TODO: print results


def show_result(suites, result):
    suite = select_suite(suites, result['suite_id'])
    try:
        suite.show(result)
    except:
        traceback.print_exc()
        msg = 'Error when attempting to show "{}"'
        raise AbortError(msg.format(print_resultspec(result)))


def diff_results(suites, golden_result, result):
    suite_id = result['suite_id']
    golden_suite_id = golden_result['result_id']

    if golden_suite_id != suite_id:
        msg = 'Can not diff results from different suites "{}" and "{}"'
        raise AbortError(msg.format(golden_suite_id, suite_id))

    suite = select_suite(suites, suite_id)
    try:
        suite.diff(golden_result, result)
    except:
        traceback.print_exc()
        msg = 'Error when attempting to show "{}"'
        raise AbortError(msg.format(print_resultspec(result)))

