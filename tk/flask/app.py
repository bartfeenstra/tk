from flask import Flask, request, Response
from requests_futures.sessions import FuturesSession
from werkzeug.exceptions import NotAcceptable, UnsupportedMediaType, NotFound, \
    BadRequest

from tk.process import Process


def request_content_type(content_type):
    """
    Check we can accept the request body.
    :param content_type:
    :return:
    """

    def decorator(route_method):
        def checker(*route_method_args, **route_method_kwargs):
            if request.mimetype != content_type:
                raise UnsupportedMediaType()
            return route_method(*route_method_args, **route_method_kwargs)

        return checker

    return decorator


def response_content_type(content_type):
    """
    Check we can deliver the right content type.
    :return:
    """

    def decorator(route_method):
        def checker(*route_method_args, **route_method_kwargs):
            negotiated_content_type = request.accept_mimetypes.best_match(
                [content_type])
            if negotiated_content_type is None:
                raise NotAcceptable()
            return route_method(*route_method_args, **route_method_kwargs)

        return checker

    return decorator


class App(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__('tk', static_folder=None, *args, **kwargs)
        self.config.from_object('tk.default_config')
        self.config.from_envvar('TK_CONFIG_FILE')
        self._register_routes()
        self._session = FuturesSession()
        self._process = Process(self._session, self.config['SOURCEBOX_URL'],
                                self.config['SOURCEBOX_ACCOUNT_NAME'],
                                self.config['SOURCEBOX_USER_NAME'],
                                self.config['SOURCEBOX_PASSWORD'])

    def _register_routes(self):
        @self.route('/submit', methods=['POST'], endpoint='submit')
        @request_content_type('application/octet-stream')
        @response_content_type('text/plain')
        def submit():
            document = request.get_data()
            if not document:
                raise BadRequest()
            process_id = self._process.submit(document)
            return Response(process_id, 200, mimetype='text/plain')

        @self.route('/retrieve/<process_id>', endpoint='retrieve')
        @request_content_type('')
        @response_content_type('text/xml')
        def retrieve(process_id):
            result = self._process.retrieve(process_id)
            if result is None:
                raise NotFound()
            return Response(result, 200, mimetype='text/plain')
