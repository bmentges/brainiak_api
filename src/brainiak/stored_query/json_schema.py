query_crud_schema = {
    "type": "object",
    "additionalProperties": False,
    "required": ["sparql_template", "description"],
    "properties": {
        "sparql_template": {"type": "string"},
        "description": {"type": "string"}
    }
}


result_response_schema = {
    "response": {
        "type": "object",
        "required": ["items"],
        "properties": {
            "items": {"type": "object"}
        }
    }
}
