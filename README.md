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
In order to send a specific response back to a specific request you'll need to create a JSON file that tells sham how to respond to particular requests.
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
The value for each path should be another JSON object with two keys, `args` and `response`.
The `args` key is a JSON object that represents the query string on the URL.
The `response` key can be a JSON object or a string.
When a HTTP request matches the path and query string sham will return the response object.

### TODO:
* Add `method` key to JSON so we can return different responses based on request method
* Add `headers` key so responses can have specific headers sent back (i.e. Content-type)
* Allow template files to be used for responses
* Allow default response no matter what query args are sent

