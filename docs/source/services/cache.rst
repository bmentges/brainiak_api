Caching
=======

Cache is enabled or disabled at the settings.py of the application, throught the variable ENABLE_CACHE.
Despite this global control, cache is set (or not) for each resource of the API.
To check if cache is enabled for some primitive, run:

curl -i -X OPTIONS http://localhost:5100/

If cache is enabled, "PURGE" will be shown on the response header "Access-Control-Allow-Methods".


Resource cache status
---------------------

It is possible to check the cache status of a certain resource by the following headers:

 * X-Cache: tells if there was a HIT (cached data) or MISS (fresh data) at Brainiak API
 * Last-Modified: date and time the response was computed. This is specialy useful when X-Cache returns HIT.


Purge
-----

To cleanup cache, the PURGE method should be used:

Example:

curl -i -X PURGE http://localhost:5100/

Note that for purging purposes, query string parameters are ignored.


Recursive purge
---------------

It is also possible to cleanup recursivelly, calling PURGE with the header "X-Cache-Recursive" set to 1:

curl -i -X PURGE  --header "X-Cache-Recursive: 1" http://localhost:5100/

Carefull when using this feature, all cached resources from that point on will be purged.

For example, if the following keys were cached:

a. http://localhost:5100/
b. http://localhost:5100/person/
c. http://localhost:5100/person/Person
d. http://localhost:5100/person/Person/IsaacNewton

And it is called:

curl -i -X PURGE  --header "X-Cache-Recursive: 1" http://localhost:5100/person/

Both (b), (c) and (d) will be purged.


Otherwise, if:

curl -i -X PURGE  --header "X-Cache-Recursive: 1" http://localhost:5100/person/Person

Only (c) and (d) will be purged.