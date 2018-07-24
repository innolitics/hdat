import argparse
import traceback
import sys

from .resultspec import resolve_resultspecs, print_resultspec
from .casespec import resolve_casespecs, select_suite
from .runner import run_cases
from .util import AbortError
from collections import defaultdict
from functools import reduce


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(prog='hdat')
    subparsers = parser.add_subparsers(dest='command', metavar='<command>')

    list_help = 'list available cases, collected in the current working dir'
    list_parser = subparsers.add_parser('list', help=list_help)
    list_parser.add_argument('casespecs', nargs='*', default=[''], metavar='<case>')

    run_help = 'run cases, store results in archive, compare against goldens'
    run_parser = subparsers.add_parser('run', help=run_help)
    run_case_help = 'case specifier to run'
    run_parser.add_argument('casespecs', nargs='*', default=[''], metavar='<case>', help=run_case_help)

    show_help = 'visualize a single result'
    show_parser = subparsers.add_parser('show', help=show_help)
    show_result_help = 'result specifier to show'
    show_parser.add_argument('resultspec', nargs='*', default='', metavar='<result>', help=show_result_help)

    runshow_help = 'run then visualize a single result'
    runshow_parser = subparsers.add_parser('runshow', help=runshow_help)
    runshow_case_help = 'case specifier to run and show results'
    runshow_parser.add_argument('casespecs', nargs='*', default='', metavar='<case>', help=runshow_case_help)

    diff_help = 'compare two results'
    diff_parser = subparsers.add_parser('diff', help=diff_help)
    diff_result_help = 'results being compared'
    diff_parser.add_argument('resultspec', nargs=2, metavar='<result>', help=diff_result_help)

    verify_help = 'move result metrics from archive to the golden store'
    verify_parser = subparsers.add_parser('verify', help=verify_help)
    verify_result_help = 'results to be stripped and moved into the golden store'
    verify_parser.add_argument('resultspec', nargs='?', default='', metavar='<result>', help=verify_result_help)

    csv_help = 'print results into a CSV'
    csv_parser = subparsers.add_parser('csv', help=csv_help)
    csv_result_help = 'results to be printed'
    csv_parser.add_argument('resultspec', nargs='?', default='', metavar='<result>', help=csv_result_help)
    csv_keys_help = 'keys specifier to print data (\'*\' may be used as a wildcard)'
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
        for resultspec in args.resultspec:
            results = resolve_resultspecs(archive, resultspec)
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
        print_results(results, args.keys)


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


def get_result_keys(result, input_key_list):
    keys = []
    for in_key in input_key_list:
        if "." in in_key:
            base_in_key, nested_in_key = in_key.split(".")
            if nested_in_key == "*":
                if base_in_key in result.keys() and isinstance(result[base_in_key], dict):
                    for nested_key in result[base_in_key].keys():
                        keys.append(".".join([base_in_key, nested_key]))
            else:
                if base_in_key in result.keys() and isinstance(result[base_in_key], dict):
                    if nested_in_key in result[base_in_key].keys():
                        keys.append(".".join([base_in_key, nested_in_key]))
        elif in_key in result.keys():
            keys.append(in_key)
    return sorted(keys)


def get_unused_keys(input_key_list, distinct_keys):
    unused_keys = list(set(input_key_list)-set(distinct_keys))
    wildcard_keys = filter((lambda x: ".*" in x), unused_keys)
    for undefined_key in wildcard_keys:
        base_key, _ = undefined_key.split(".")
        for key in distinct_keys:
            if base_key in key and "." in key:
                unused_keys.remove(undefined_key)
                break
    return sorted(unused_keys)


def get_result_data(key, result):
    if "." in key:
        base_key, nested_key = key.split(".")
        if isinstance(result[base_key], dict):
            if nested_key in result[base_key].keys():
                return str(result[base_key][nested_key])
    else:
        return str(result[key])


def build_result_csv_dict(distinct_keys, all_data):
    results_dict = defaultdict()
    for result_keys, result_values in all_data:
        for key in distinct_keys:
            if key in result_keys:
                results_dict.setdefault(key, []).append(result_values[result_keys.index(key)])
            else:
                results_dict.setdefault(key, []).append(" ")
    return results_dict


def print_results(results, input_keys_str):
    if not input_keys_str:
        input_keys_str = 'case_id,result_id,ran_on,commit,metrics.*'
    input_key_list = [key.strip() for key in input_keys_str.split(",")]

    all_data = []
    for result in results:
        result_keys = get_result_keys(result, input_key_list)
        data_list = [get_result_data(key, result) for key in result_keys]
        all_data.append((result_keys, data_list))

    keys_set = [set(result_keys) for result_keys, _ in all_data]
    distinct_keys = sorted(list(reduce(set.union, keys_set)))
    results_dict = build_result_csv_dict(distinct_keys, all_data)
    keys_not_found = get_unused_keys(input_key_list, distinct_keys)

    if keys_not_found:
        err_out = ", ".join(keys_not_found)
        sys.stderr.write("Keys not found: {}\n".format(err_out))

    if distinct_keys:
        keys_out = ", ".join(distinct_keys)
        print(keys_out)

    data_list = []
    for i in range(len(all_data)):
        for key in distinct_keys:
            data_list = [results_dict[key][i] for key in distinct_keys]
        if data_list:
            data_out = ", ".join(data_list)
            print(data_out)
