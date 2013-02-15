# coding: utf-8


def filter_values(result_dict, key):
    results = []
    for item in result_dict['results']['bindings']:
        if item.get(key):
            result = item[key]['value']
            results.append(result)
    return results


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
        simplified_ranges = get_ranges(original_ranges_dict)
        if simplified_ranges:
            simplified_dict[predicate_uri]["ranges"] = simplified_ranges

        simplified_graphs = get_ranges_graphs(original_ranges_dict)
        if simplified_graphs:
            simplified_dict[predicate_uri]["graphs"] = simplified_graphs

    return simplified_dict


def get_ranges_graphs(ranges_dict):
    graphs_set = set([])
    for range_values in ranges_dict.values():
        graph_uri = range_values.get("graph")
        if graph_uri:
            graphs_set.add(graph_uri)
    return list(graphs_set)


def get_ranges(ranges_dict):
    return ranges_dict.keys()


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


class PredicateResultHandler():

    def __init__(self, class_uri, class_attributes, predicates, cardinalities):
        self.query_result = predicates
        self.cardinalities = CardinalityResultHandler(cardinalities).get_cardinalities()
        self.class_uri = class_uri
        self.class_result = class_attributes

    def get_complete_dict(self):
        complete_dict = {"class": self.class_uri,
                         "label": get_one_value(self.class_result, "label"),
                         "comment": get_one_value(self.class_result, "comment"),
                         "predicates": self.get_predicates_and_cardinalities_dict()}

        return complete_dict

    def get_predicates_and_cardinalities_dict(self):
        predicates = self.get_unique_predicates_list()
        predicates_dict = {}

        for predicate in predicates:
            new_ranges = {}
            predicate_dict = {}
            ranges = self.get_ranges_for_predicate(predicate)
            for predicate_range in ranges:
                new_ranges[predicate_range] = ranges[predicate_range]
                if predicate in self.cardinalities and predicate_range in self.cardinalities[predicate]:
                    predicate_restriction = self.cardinalities[predicate]
                    new_ranges[predicate_range].update(predicate_restriction[predicate_range])
                    if "options" in predicate_restriction:
                        new_ranges[predicate_range]["options"] = predicate_restriction["options"]

            predicate_dict["range"] = new_ranges
            for item in self.get_predicates_dict_for_a_predicate(predicate):
                predicate_dict["type"] = item["type"]
                predicate_dict["label"] = item["label"]
                predicate_dict["graph"] = item["predicate_graph"]
                if "predicate_comment" in item:  # Para Video que não tem isso
                    predicate_dict["comment"] = item["predicate_comment"]
            predicates_dict[predicate] = predicate_dict

        return predicates_dict

    def get_unique_predicates_list(self):
        unique_predicates = []
        for item in self.query_result['results']['bindings']:
            predicate = item['predicate']['value']
            if not predicate in unique_predicates:
                unique_predicates.append(predicate)

        unique_predicates.sort()
        return unique_predicates

    def get_predicates_dict_for_a_predicate(self, predicate):
        items = []
        parsed_item = {}
        for item in self.query_result['results']['bindings']:
            if item['predicate']['value'] == predicate:
                for attribute in item:
                    if attribute not in parsed_item:
                        parsed_item[attribute] = item[attribute]['value']
                items.append(parsed_item)

        return items

    def get_ranges_for_predicate(self, predicate):
        ranges = {}
        for item in self.query_result['results']['bindings']:
            if item['predicate']['value'] == predicate:
                range_class_uri = item['range']['value']
                range_label = item.get('label_do_range', {}).get('value', "")
                range_graph = item.get('grafo_do_range', {}).get('value', "")
                ranges[range_class_uri] = {'graph': range_graph, 'label': range_label}
        return ranges
