Using HTTP methods in a RESTful way
===================================

The HTTP verbs comprise a major portion of our “uniform interface” goal.
They represent the actions applied over the resources provided by the interface.

The primary or most commonly used HTTP verbs (or methods) are POST, GET, PUT, and DELETE.
These correspond to create, read, update, and delete (or CRUD) operations, respectively.
There are a number of other verbs, too, but are utilized less frequently such as OPTIONS and HEAD.

**HEAD**

Can be issued against any resource to get just the HTTP header info.


**GET**

Used for retrieving resources.

**POST**

Used for creating resources subordinate to a target collection.

**PUT**

Used for defining/replacing resources or collections.
For PUT requests with no <code>body</code> attribute, be sure to set the <code>Content-Length</code> header to zero.

**DELETE**

Used for deleting resources.

**PATCH**

Used for updating resources with partial JSON data.  For instance, an
Issue resource has <code>title</code> and <code>body</code> attributes.  A PATCH request may
accept one or more of the attributes to update the resource.  PATCH is a
relatively new and uncommon HTTP verb, so resource endpoints also accept
POST requests.
