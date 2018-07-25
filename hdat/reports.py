import csv
import sys

from collections import defaultdict
from itertools import chain


def expand_key_parts(result, nested_key):
    if nested_key[-1] == "*":
        nested_data = get_nested_item(result, nested_key[:-1])
        if isinstance(nested_data, dict):
            for key in nested_data:
                yield nested_key[:-1] + [key]
    else:
        yield nested_key


def get_nested_item(result, nested_key):
    num_levels = len(nested_key)
    try:
        if num_levels == 0 or nested_key[0] not in result:
            return
        elif num_levels == 1:
            return result[nested_key[0]]
        else:
            return get_nested_item(result[nested_key[0]], nested_key[1:])
    except TypeError:
        return


def print_results(results, input_keys_str):
    if not input_keys_str:
        input_keys_str = 'case_id,result_id,ran_on,commit,metrics.*'
    reader_keys = csv.reader([input_keys_str])
    input_keys = [key.strip() for key in list(reader_keys)[0]]
    key_parts = [key.split('.') for key in input_keys]

    keys = set()
    all_result_data = []
    for result in results:
        result_data = defaultdict(lambda: '')
        expanded_keys_gens = [expand_key_parts(result, ks) for ks in key_parts]
        expanded_keys = chain.from_iterable(expanded_keys_gens)
        for expanded_key in expanded_keys:
            result_key = '.'.join(expanded_key)
            keys.add(result_key)
            result_data[result_key] = get_nested_item(result, expanded_key)
        all_result_data.append(result_data)

    output_writer = csv.writer(sys.stdout)
    sorted_keys = sorted(list(keys))
    output_writer.writerow(sorted_keys)
    for result_data in all_result_data:
        data_out = [result_data[key] for key in sorted_keys]
        output_writer.writerow(data_out)
