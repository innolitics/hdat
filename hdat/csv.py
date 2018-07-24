from collections import defaultdict
from itertools import chain


def expand_key_specifier(result, nested_key):
    if nested_key[-1] == "*":
        nested_data = get_nested_item(result, nested_key[:-1])
        if isinstance(nested_data, dict):
            for key in nested_data:
                yield nested_key[:-1] + [key]
    else:
        yield nested_key


def get_nested_item(result, nested_key):
    num_levels = len(nested_key)
    if nested_key[0] not in result:
        return ''
    elif num_levels == 0:
        return
    elif num_levels == 1:
        return result[nested_key[0]]
    else:
        return get_nested_item(result[nested_key[0]], nested_key[1:])


def print_results(results, input_keys_str):
    if not input_keys_str:
        input_keys_str = 'case_id,result_id,ran_on,commit,metrics.*'
    input_keys = [key.strip() for key in input_keys_str.split(",")]
    key_specifiers = [key.split(".") for key in input_keys]

    keys = set()
    all_data = []
    for result in results:
        result_data = defaultdict(lambda: '')
        expanded_keys_generator = [expand_key_specifier(result, ks) for ks in key_specifiers]
        expanded_keys = chain.from_iterable(expanded_keys_generator)
        for expanded_key in expanded_keys:
            result_key = '.'.join(expanded_key)
            keys.add(result_key)
            result_data[result_key] = get_nested_item(result, expanded_key)
        all_data.append(result_data)

    sorted_keys = sorted(list(keys))
    print(", ".join(sorted_keys))
    for result_data in all_data:
        data_out = [str(result_data[key]) for key in sorted_keys]
        print(", ".join(data_out))
