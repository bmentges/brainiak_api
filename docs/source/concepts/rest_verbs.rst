Using HTTP methods in a RESTful way
===================================

The HTTP verbs comprise a major portion of our “uniform interface” constraint and provide us the action counterpart to the noun-based resource. The primary or most-commonly-used HTTP verbs (or methods, as they are properly called) are POST, GET, PUT, and DELETE. These correspond to create, read, update, and delete (or CRUD) operations, respectively. There are a number of other verbs, too, but are utilized less frequently. Of those less-frequent methods, OPTIONS and HEAD are used more often than others.

**HEAD**

Can be issued against any resource to get just the HTTP header info.


**GET**

Used for retrieving resources.

**POST**

Used for creating resources, or performing custom actions (such as
merging a pull request).

**PATCH**

Used for updating resources with partial JSON data.  For instance, an
Issue resource has <code>title</code> and <code>body</code> attributes.  A PATCH request may
accept one or more of the attributes to update the resource.  PATCH is a
relatively new and uncommon HTTP verb, so resource endpoints also accept
POST requests.

**PUT**

Used for replacing resources or collections. For PUT requests
with no <code>body</code> attribute, be sure to set the <code>Content-Length</code> header to zero.

**DELETE**

Used for deleting resources.

Below is a table summarizing recommended return values of the primary HTTP methods in combination with the resource URIs:

+----------+---------------------------------------------------------------------+-------------------------------------+
|  HTTP    | Entire Collection                                                   | Specific Item                       |
|  Verb    | (e.g. /place/City)                                                  | (e.g. /place/City/{id})             |
+==========+=====================================================================+=====================================+
| GET      | 200 (OK), list of cities. Use pagination, sorting and filtering     | 200 (OK), single city.              |
|          | to navigate big lists.                                              | 404 (Not Found), if ID not found or |
|          |                                                                     | invalid.                            |
+----------+---------------------------------------------------------------------+-------------------------------------+
| PUT	   | 404 (Not Found), unless you want to update/replace every resource in| 200 (OK) or 204 (No Content).       |
|          | the entire collection.	                                             | 404 (Not Found), if ID not found or |
|          |                                                                     | invalid.                            |
+----------+---------------------------------------------------------------------+-------------------------------------+
| POST	   | 201 (Created), 'Location' header with link to /place/City/{id}      | 404 (Not Found).                    |
|          | containing new ID.	                                                 |                                     |
+----------+---------------------------------------------------------------------+-------------------------------------+
| DELETE   | 404 (Not Found), unless you want to delete the whole collection—not | 200 (OK). 404 (Not Found), if ID not|
|          | often desirable.	                                                 | found or invalid.                   |
+----------+---------------------------------------------------------------------+-------------------------------------+

