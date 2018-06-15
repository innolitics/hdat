import argparse
import traceback

from .resultspec import resolve_resultspecs, print_resultspec
from .casespec import resolve_casespecs, select_suite
from .runner import run_cases
from .util import AbortError


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='hdat')
    subparsers = parser.add_subparsers(dest='command', metavar='<command>')

    list_help = 'list available cases, collected in the current working dir'
    list_parser = subparsers.add_parser('list', help=list_help)
    list_parser.add_argument('casespecs', nargs='*', default=[''], metavar='<case>')

    run_help = 'run cases, store results in archive, compare against goldens'
    run_parser = subparsers.add_parser('run', help=run_help)
    run_parser.add_argument('casespecs', nargs='*', default=[''], metavar='<case>')

    show_help = 'visualize a single result'
    show_parser = subparsers.add_parser('show', help=show_help)
    show_result_help = 'result specifier to show'
    show_parser.add_argument('resultspec', nargs="?", default='', metavar='<result>', help=show_result_help)

    runshow_help = 'run then visualize a single result'
    runshow_parser = subparsers.add_parser('runshow', help=runshow_help)
    runshow_parser.add_argument('casespecs', nargs=1, default='', metavar='<result>')

    diff_help = 'compare two results'
    diff_parser = subparsers.add_parser('diff', help=diff_help)
    diff_result_help = 'results being compared'
    diff_parser.add_argument('resultspec', nargs=2, metavar='<result>', help=diff_result_help)

    verify_help = 'move result metrics from archive to the golden store'
    verify_parser = subparsers.add_parser('verify', help=verify_help)
    verify_result_help = 'results to be stripped and moved into the golden store'
    verify_parser.add_argument('resultspec', nargs='?', default='', metavar='<result>', help=verify_result_help)

    # we should think through the command line API for this; we should try to
    # mimick how other command line tools handle letting users select keys from a list;
    # I do like the idea of printing the results to standard output; this lets
    # the user redirect the result to a file, or just look at the output during
    # interactive use of hdat
    csv_help = 'print results into a CSV'
    csv_parser = subparsers.add_parser('csv', help=csv_help)
    csv_result_help = 'results to be printed'
    csv_parser.add_argument('resultspec', nargs='?', default='', metavar='<result>', help=csv_result_help)

    return parser.parse_args(arguments)


def _format_cases_status(cases_status):
    return 'PASS: {}, FAIL: {}, UNKNOWN: {}, ERROR: {}'.format(
        cases_status['pass'],
        cases_status['fail'],
        cases_status['unknown'],
        cases_status['error'],
    )


def hdat_cli(arguments, suites, golden_store, archive, git_info):
    args = parse_arguments(arguments)

    if args.command is None:
        parse_arguments(['-h'])

    if args.command == 'list':
        cases = resolve_casespecs(suites, args.casespecs)
        print("\n".join(['{}/{}'.format(suite_id, case_id) for suite_id, case_id in cases]))
    elif args.command == 'run':
        cases = resolve_casespecs(suites, args.casespecs)
        cases_status = run_cases(suites, golden_store, archive, git_info, cases)
        if cases_status['pass'] < len(cases):
            raise AbortError(_format_cases_status(cases_status))
    elif args.command == 'show':
        results = resolve_resultspecs(archive, args.resultspec)
        for result in results:
            show_result(suites, result)
    elif args.command == 'runshow':
        cases = resolve_casespecs(suites, args.casespecs)
        cases_status = run_cases(suites, golden_store, archive, git_info, cases)
        if cases_status['error'] > 0:
            raise AbortError(_format_cases_status(cases_status))
        for casespec in args.casespecs:
            results = resolve_resultspecs(archive, casespec)
            for result in results:
                show_result(suites, result)
    elif args.command == 'diff':
        golden_results = resolve_resultspecs(archive, args.resultspec[0])
        results = resolve_resultspecs(archive, args.resultspec[1])
        for golden_result, result in zip(golden_results, results):
            diff_results(suites, golden_result, result)
    elif args.command == 'verify':
        results = resolve_resultspecs(archive, args.resultspec)
        for result in results:
            golden_store.insert(result)
    elif args.command == 'csv':
        results = resolve_resultspecs(archive, args.resultspec)
        print_results(results)



def show_result(suites, result):
    suite = select_suite(suites, result['suite_id'])
    try:
        suite.show(result)
    except Exception as e:
        traceback.print_exc()
        msg = 'Error when attempting to show "{}": {}'
        raise AbortError(msg.format(print_resultspec(result), e))


def diff_results(suites, golden_result, result):
    suite_id = result['suite_id']
    golden_suite_id = golden_result['suite_id']

    if golden_suite_id != suite_id:
        msg = 'Can not diff results from different suites "{}" and "{}"'
        raise AbortError(msg.format(golden_suite_id, suite_id))

    suite = select_suite(suites, suite_id)
    try:
        suite.diff(golden_result, result)
    except Exception as e:
        traceback.print_exc()
        msg = 'Error when attempting to show "{}": {}'
        raise AbortError(msg.format(print_resultspec(result), e))


def print_results(results):
    # this needs to be made much more general
    keys = [
        'suite_id',
        'result_id',
        'case_input.phantom',
        'case_input.modality',
        'metrics.TPF',
        'metrics.FPF',
        'metrics.max_distortion',
        'metrics.99_distortion',
        'metrics.95_distortion',
        'metrics.90_distortion',
        'metrics.mean_distortion',
        'metrics.median_distortion',
        'metrics.min_distortion',
    ]
    print(", ".join(keys))
    for result in results:
        data = [
            result['suite_id'],
            result['result_id'],
            result['case_input']['phantom_model'],
            result['case_input']['modality'],
            result['metrics']['TPF'],
            result['metrics']['FPF'],
            result['metrics']['max_distortion'],
            result['metrics']['99_distortion'],
            result['metrics']['95_distortion'],
            result['metrics']['90_distortion'],
            result['metrics']['mean_distortion'],
            result['metrics']['median_distortion'],
            result['metrics']['min_distortion'],
        ]
        data = [str(d) for d in data]
        print(", ".join(data))
