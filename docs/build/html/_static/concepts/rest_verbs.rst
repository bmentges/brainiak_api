Using HTTP methods in a RESTful way
===================================

The HTTP verbs comprise a major portion of our “uniform interface” goal.
They represent the actions applied over the resources provided by the interface.

The primary or most commonly used HTTP verbs (or methods) are ``POST``, ``GET``, ``PUT``, and ``DELETE``.
These correspond to create, read, update, and delete (or CRUD) operations, respectively.
There are a number of other verbs, too, but are utilized less frequently such as ``OPTIONS``, ``HEAD`` and ``PURGE``.

Below is a table summarizing recommended return values of the primary HTTP methods in combination with the resource URIs:


+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
|  HTTP                                             | Entire Collection                             | Specific Item                       |
|  Verb                                             | (e.g. /place/City)                            | (e.g. /place/City/{id})             |
+===================================================+===============================================+=====================================+
| ``HEAD`` can be issued against any resource to    |                                               |                                     |
| get just the HTTP header info.                    |                                               |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``GET`` for retrieving resources.                 | 200 (OK), list of cities. Use pagination,     | 200 (OK), single city.              |
|                                                   | sorting and filtering to navigate big lists.  | 404 (Not Found), if ID not found or |
|                                                   |                                               | invalid.                            |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``PUT`` for replacing resources.                  | 404 (Not Found)                               | 200 (OK) or 204 (No Content).       |
|                                                   |                                               | 404 (Not Found), if ID not found or |
|                                                   |                                               | invalid.                            |
|                                                   |                                               |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``POST`` for creating resources                   | 201 (Created), 'Location' header with link to | 404 (Not Found).                    |
|                                                   | /place/City/{id} containing new ID.           |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``DELETE`` for deleting resources.                | 404 (Not Found)                               | 204 (No Content, resource deleted). |
|                                                   |                                               | 404 (Not Found), if ID              |
|                                                   |                                               | not found or invalid.               |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
