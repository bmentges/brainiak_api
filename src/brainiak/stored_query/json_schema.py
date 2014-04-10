query_crud_schema = {
    "type": "object",
    "required": ["sparql_template", "description"],
    "additionalProperties": True,
    "properties": {
        "sparql_template": {"type": "string"},
        "description": {"type": "string"},
        "response_fields": {"type": "array"}
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
