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
    csv_keys_help = 'keys specifier to print data'
    csv_parser.add_argument('--keys', nargs='?', dest='keys', help=csv_keys_help)

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
        for result in results:
            print_result(result, args.keys)


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


def get_result_data(result, input_key_list):
    keys = []
    data = []

    for key, value in result.items():
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                joined_key = ".".join([key, nested_key])
                if "".join([key, ".*"]) in input_key_list:
                    keys.append(joined_key)
                    data.append(nested_value)
                elif joined_key in input_key_list:
                    keys.append(joined_key)
                    data.append(nested_value)
        else:
            if "context" not in key and key in input_key_list:
                keys.append(key)
                data.append(value)

    return keys, data


def get_wrong_keys(input_key_list, result_keys):
    wrong_keys = []

    for in_key in input_key_list:
        if in_key not in result_keys:
            matched_joined_keys = [key for key in result_keys if in_key.replace("*", "") in key]
            if ".*" not in in_key or not matched_joined_keys:
                wrong_keys.append(in_key)

    return ", ".join(wrong_keys)


def print_result(result, input_keys_str):
    if not input_keys_str:
        input_keys_str = 'case_id,result_id,run_on,gith_hash,metrics.*'
    
    input_key_list = input_keys_str.split(",")

    result_keys, result_data = get_result_data(result, input_key_list)

    wrong_keys = get_wrong_keys(input_key_list, result_keys)

    data_str = [str(value) for value in result_data]
    keys_out = ", ".join(result_keys)
    data_out = ", ".join(data_str)

    if keys_out:
        print("Matched data in suite {} case {}.".format(result["suite_id"], result["case_id"]))
        print(keys_out)
        print(data_out)
    else:
        print("No keys matched data in suite {} case {}.".format(result["suite_id"], result["case_id"]))

    if wrong_keys:
        print("Keys not found: {}".format(wrong_keys))
