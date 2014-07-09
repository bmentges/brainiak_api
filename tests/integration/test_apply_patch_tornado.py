# Util tornado 3.1.0.0, tornado.curl_httpclient ignores payloads (body) of
# custom methods, some that could not be ignored such as PATCH.
#
# We fixed this and proposed a pull request to tornado:
# https://github.com/tornadoweb/tornado/pull/1090
#
# While this issue is not fixed (1/7/2014), we are monkey patching
# tornado.curl_httpclient's _curl_setup_request.


import tornado
from tests.tornado_cases import _curl_setup_request

print("Temporary mockey-patch to tornado/curl_httpclient.py")
tornado.curl_httpclient._curl_setup_request = _curl_setup_request
