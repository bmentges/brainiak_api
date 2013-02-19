# coding: utf-8


def filter_values(result_dict, key):
    return [item[key]['value'] for item in result_dict['results']['bindings'] if item.get(key)]


def get_one_value(result_dict, key):
    values = filter_values(result_dict, key)
    if not values:
        return False
    return values[0]


def is_result_empty(result_dict):
    return len(result_dict['results']['bindings']) == 0


def lang_dict(result_list):
    lang_dict = {}
    for result in result_list:
        splitted = result.split("@")
        try:
            lang_dict[splitted[1]] = splitted[0]
        except:  # default: pt
            lang_dict["pt"] = splitted[0]
    return lang_dict


def simplify_dict(predicate_dict):
    simplified_dict = {}
    predicates = predicate_dict["predicates"]
    for predicate_uri, predicate_values in predicates.iteritems():
        simplified_dict[predicate_uri] = {}
        original_ranges_dict = predicate_values["range"]
        simplified_ranges = original_ranges_dict.keys()
        if simplified_ranges:
            simplified_dict[predicate_uri]["ranges"] = simplified_ranges

        simplified_graphs = get_ranges_graphs(original_ranges_dict)
        if simplified_graphs:
            simplified_dict[predicate_uri]["graphs"] = simplified_graphs

    return simplified_dict


def get_ranges_graphs(ranges_dict):
    return list({range_value.get("graph") for range_value in ranges_dict.values()
                                          if range_value.get("graph")})


def parse_label_and_type(sparql_dict):
    try:
        item = sparql_dict["results"]["bindings"][0]
    except IndexError:
        return {}
    else:
        return {"label": item["label"]["value"],
                "type_label": item["type_label"]["value"]}


class CardinalityResultHandler():

    def __init__(self, query_result):
        self.query_result = query_result

    def get_cardinalities(self):
        cardinalities = {}
        for binding in self.query_result['results']['bindings']:
            property = binding["predicate"]["value"]
            range = binding["range"]["value"]
            if (not property in cardinalities or not range in cardinalities[property]) and not range.startswith("nodeID://"):
                cardinalities[property] = {range: {}}
            if "min" in binding:
                cardinalities[property][range].update({"min": binding["min"]["value"]})
            elif "max" in binding:
                cardinalities[property][range].update({"max": binding["max"]["value"]})
            elif "enumerated_value" in binding:
                new_options = cardinalities[property].get("options", [])
                new_options_entry = {binding["enumerated_value"]["value"]: binding.get("enumerated_value_label", "").get("value", "")}
                new_options.append(new_options_entry)
                cardinalities[property].update({"options": new_options})

        return cardinalities


