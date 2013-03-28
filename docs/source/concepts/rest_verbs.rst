Using HTTP methods in a RESTful way
===================================

The HTTP verbs comprise a major portion of our “uniform interface” constraint and provide us the action counterpart to
the noun-based resource. The primary or most-commonly-used HTTP verbs (or methods, as they are properly called) are ``POST``,
``GET``, ``PUT``, and ``DELETE``. These correspond to create, read, update, and delete (or CRUD) operations, respectively. There are
a number of other verbs, too, but are utilized less frequently. Of those less-frequent methods, ``OPTIONS`` and ``HEAD`` are used
more often than others.

Below is a table summarizing recommended return values of the primary HTTP methods in combination with the resource URIs:


+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
|  HTTP                                             | Entire Collection                             | Specific Item                       |
|  Verb                                             | (e.g. /place/City)                            | (e.g. /place/City/{id})             |
+===================================================+===============================================+=====================================+
| ``HEAD``, can be issued against any resource to   |                                               |                                     |
| get just the HTTP header info.                    |                                               |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``GET``, used for retrieving resources.           | 200 (OK), list of cities. Use pagination,     | 200 (OK), single city.              |
|                                                   | sorting and filtering to navigate big lists.  | 404 (Not Found), if ID not found or |
|                                                   |                                               | invalid.                            |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``PUT``, used for replacing resources.            | 404 (Not Found), unless you want to           | 200 (OK) or 204 (No Content).       |
| For ``PUT`` requests with no ``body``             | update/replace every resource in the          | 404 (Not Found), if ID not found or |
| attribute, be sure to set the                     | entire collection.                            | invalid.                            |
| ``Content-Length`` header to zero.                |                                               |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``POST``, used for creating resources, or         | 201 (Created), 'Location' header with link to | 404 (Not Found).                    |
| performing custom actions (such as merging a pull |                                               |                                     |
| request).                                         | /place/City/{id} containing new ID.           |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``DELETE``, used for deleting resources.          | 404 (Not Found), unless you want to delete    | 200 (OK). 404 (Not Found), if ID    |
|                                                   | the whole collection—not often desirable.     | not found or invalid.               |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+
| ``PATCH``, used for updating resources with       |                                               |                                     |
| partial JSON data. For instance, an Issue         |                                               | 200 (OK) or 204 (No Content).       |
| resource has ``title`` and ``body``               |                                               | 404 (Not Found), if ID not found or |
| attributes. A ``PATCH`` request may accept one or |                                               |  invalid                            |
| more of the attributes to update the resource.    |                                               |                                     |
| ``PATCH`` is a relatively new and uncommon HTTP   |                                               |                                     |
| verb, so resource endpoints also accept ``POST``  |                                               |                                     |
| requests.                                         |                                               |                                     |
+---------------------------------------------------+-----------------------------------------------+-------------------------------------+




