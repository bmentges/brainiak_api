print("Temporary mockey-patch to tornado/curl_httpclient.py")
tornado.curl_httpclient._curl_setup_request = _curl_setup_request
