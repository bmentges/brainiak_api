# coding: utf-8


def get_one_value(result_dict, key):
    values = filter_values(result_dict, key)
    if not values:
        return False
    return values[0]


def filter_values(result_dict, key):
    return [item[key]['value'] for item in result_dict['results']['bindings'] if item.get(key)]


def compress_keys_and_values(result_dict, keymap={"label": "title", "subject": "@id"}, ignore_keys=["total"]):
    result_list = []
    for item in result_dict['results']['bindings']:
        row = {}
        for key in item:
            if not key in ignore_keys:
                row[keymap.get(key, key)] = item[key]['value']
        result_list.append(row)
    return result_list


def is_result_empty(result_dict):
    return len(result_dict['results']['bindings']) == 0
