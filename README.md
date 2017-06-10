# sham
Tool used to mock HTTP servers. Records all incoming requests and can send fake responses.


# Requirements
* Python 3, because it's 2017
* The modules in requirements.txt

# Installation
* Clone repo
* Create virtualenv `virtualenv -p python3 env`
* Install requirements: `pip install -r requirements.txt`

# Usage
### Basic Usage
* Activate virtualenv: `source env/bin/activate`
* Start server: `python main.py 6000`
  * This starts the server on localhost with port 6000. You may change it to any port you like
* Navigate to `http://localhost:6000`, notice there are no requests captured yet
* Send an HTTP request to any URL that is not the index page, i.e. `http://localhost:6000/some/example/url`
* Refresh `http://localhost:6000`, view the details of the request.

### Custom Responses
In order to send a specific response back to a specific request you'll need to create a JSON file that tells sham how
to respond to particular requests.
The file should have a JSON object inside that looks like this:

```json
{
  "some/example/url": [{
    "args": {},
    "response": {
      "example": "response with no args"
    }
  }, {
    "args": {"hello": ["world"]},
    "response": {
      "example": "response with query args ?hello=world"
    }
  }],
  "some/other/example/url": [{
    "args": {},
    "response": {
      "data": ["Look at me I'm a response!"]
    }
  }]
}
```

Each key in the JSON object should be a path, not including the base URL `localhost:6000` (without a leading `/`).
    * This path allows for basic pattern matching with regexes, See python re documentation on expected syntax.
    * If using named groups, those groups are captured and can optionally be returned in the response, see examples.
The value for each path should be another JSON object with two keys, `args` and `response`.
The `args` key is a JSON object that represents the query string on the URL. '*' will match any input arguments.
The `response` key can be a JSON object or a string.
The `method` key is a list (lowercase) of allowed HTTP methods for the response. If not provided, or specified as '*',
    the allowed methods will default to ['put', 'post', 'patch', 'get', 'delete'].
The `status_code` key should be an integer representing the HTTP return code of the response. Defaults to 200.
When a HTTP request matches the path, query, and method string sham will return the response object.
    * If path is not found a 404 will be returned, otherwise if no match is found a 405 will be returned.

### TODO:
* Add `headers` key so responses can have specific headers sent back (i.e. Content-type)
* Allow template files to be used for responses


