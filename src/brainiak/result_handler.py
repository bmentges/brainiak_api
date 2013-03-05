# coding: utf-8


def get_one_value(result_dict, key):
    values = filter_values(result_dict, key)
    if not values:
        return False
    return values[0]


def filter_values(result_dict, key):
    return [item[key]['value'] for item in result_dict['results']['bindings'] if item.get(key)]


def is_result_empty(result_dict):
    return len(result_dict['results']['bindings']) == 0
