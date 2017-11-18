# TK

[![Build Status](https://travis-ci.org/bartfeenstra/tk.svg?branch=master)](https://travis-ci.org/bartfeenstra/tk) [![Coverage Status](https://coveralls.io/repos/github/bartfeenstra/tk/badge.svg?branch=master)](https://coveralls.io/github/bartfeenstra/tk?branch=master)

## Usage
Substitute `http://127.0.0.1:5000` for the actual application URL, if
you are not using `./bin/run-dev`.

### Submitting a document
`curl -X POST --header "Content-Type: application/octet-stream" --header "Accept: text/plain" http://127.0.0.1:5000/submit`

### Retrieving a document
`curl -X GET --header "Accept: text/xml" http://127.0.0.1:5000/retrieve/{uuid}`
where `{uuid}` is the process UUID returned by `POST /submit`.

## Development

### Building the code
Run `./bin/build-dev`.

### Testing the code
Run `./bin/test`.

### Fixing the code
Run `./bin/fix` to fix what can be fixed automatically.

### Running the application
Run `./bin/run-dev` to start a development web server at
[http://127.0.0.1:5000](http://127.0.0.1:5000).

### Code style
All code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/).
