When the test test_dummy_query (tests.integration.test_query.DummyQueryTestCase)
fails with the message: IOError: [Errno 13] Permission denied

One should fixed it by adding reading and writing permissions to the appropriate directory,
for example: 
sudo chmod a+rw /usr/local/virtuoso-opensource/var/lib/virtuoso/db/
