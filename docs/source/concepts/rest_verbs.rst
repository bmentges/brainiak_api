Using HTTP methods in a RESTful way
===================================

The HTTP verbs comprise a major portion of our “uniform interface” constraint and provide us the action counterpart to the noun-based resource. The primary or most-commonly-used HTTP verbs (or methods, as they are properly called) are POST, GET, PUT, and DELETE. These correspond to create, read, update, and delete (or CRUD) operations, respectively. There are a number of other verbs, too, but are utilized less frequently. Of those less-frequent methods, OPTIONS and HEAD are used more often than others.

Below is a list summarizing recommended return values of the primary HTTP methods in combination with the resource URIs:

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
