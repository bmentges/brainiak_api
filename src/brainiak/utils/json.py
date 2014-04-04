import ujson as json

from jsonschema import validate, ValidationError
from tornado.web import HTTPError

from brainiak.utils.i18n import _


def validate_json_schema(request_json, schema):
    try:
        validate(request_json, schema)
    except ValidationError as ex:
        raise HTTPError(400, log_message=_(u"JSON not according to JSON schema definition.\n {0:s}").format(ex))


def get_json_request_as_dict(json_request_body):
    try:
        raw_body_params = json.loads(json_request_body)
    except ValueError:
        error_message = _("JSON malformed. Received: {0}.")
        raise HTTPError(400, log_message=error_message.format(json_request_body))
    return raw_body_params
