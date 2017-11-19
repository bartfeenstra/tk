# TK

[![Build Status](https://travis-ci.org/bartfeenstra/tk.svg?branch=master)](https://travis-ci.org/bartfeenstra/tk) [![Coverage Status](https://coveralls.io/repos/github/bartfeenstra/tk/badge.svg?branch=master)](https://coveralls.io/github/bartfeenstra/tk?branch=master)

## Requirements
Python 3.5+.

## Installation
Copy `./tk/default_config.py` to `./config.py`, and override any of the
default configuration as necessary.

## Usage
Substitute `http://127.0.0.1:5000` for the actual application URL, if
you are not using `./bin/run-dev`.

### Obtaining an access token
`curl -X GET --header "Accept: text/plain" --header "Authorization: Basic {credentials}" http://127.0.0.1:5000/accesstoken`
where `{credentials}` are a base64-encoded HTTP Basic Authentication
user name and password.

### Submitting a document
`curl -X POST --header "Content-Type: application/octet-stream" --data-binary @{file_path} http://127.0.0.1:5000/submit?access_token={access_token}`
where `{file_path}` is file path of the document to process, and
`{access_token}` is the access token received from `/accesstoken`.

### Retrieving a document's profile
`curl -X GET --header "Accept: text/xml" http://127.0.0.1:5000/retrieve/{uuid}?access_token={access_token}`
where `{uuid}` is the process UUID returned by `POST /submit`, and
`{access_token}` is the access token received from `/accesstoken`.

## Development

### Building the code
If you do not wish to install dependencies globally, a Virtual
Environment can be created first:
```
virtualenv -p `which python3.6` venv
. ./venv/bin/activate
```
To build the code , run `./bin/build-dev`.

### Testing the code
Run `./bin/test`.

### Fixing the code
Run `./bin/fix` to fix what can be fixed automatically.

### Running the application
Run `./bin/run-dev` to start a development web server at
[http://127.0.0.1:5000](http://127.0.0.1:5000).

### Code style
All code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/).
