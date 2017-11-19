from flask import Flask, request, Response
from flask_httpauth import HTTPBasicAuth
from requests_futures.sessions import FuturesSession
from werkzeug.exceptions import NotAcceptable, UnsupportedMediaType, NotFound, \
    BadRequest, Forbidden, Unauthorized

from tk.auth import Auth
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
        self._http_basic_auth = HTTPBasicAuth()
        self.auth = Auth(self.config['SECRET_KEY'],
                         self.config['ACCESS_TOKEN_TTL'])
        self._register_routes()
        self._session = FuturesSession()
        self.process = Process(self._session, self.config['SOURCEBOX_URL'],
                               self.config['SOURCEBOX_ACCOUNT_NAME'],
                               self.config['SOURCEBOX_USER_NAME'],
                               self.config['SOURCEBOX_PASSWORD'])

    def add_user(self, name, password):
        self.config['USERS'].append((name, password))

    def request_access_token(self, route_method):
        """
        Check the request contains a valid access token.
        :return:
        """

        def checker(*route_method_args, **route_method_kwargs):
            if 'access_token' not in request.args:
                raise Unauthorized()
            access_token = request.args.get('access_token')
            if not self.auth.verify_access_token(access_token):
                raise Forbidden()
            return route_method(*route_method_args, **route_method_kwargs)

        return checker

    def _register_routes(self):
        @self._http_basic_auth.get_password
        def _get_user_password(actual_name):
            """
            Retrieves a user's password for HTTP Basic Auth.
            :param actual_name:
            :return: The password or None if the user does not exist.
            """
            for name, password in self.config['USERS']:
                if name == actual_name:
                    return password
            return None

        @self.route('/accesstoken', endpoint='access_token')
        @self._http_basic_auth.login_required
        @request_content_type('')
        @response_content_type('text/plain')
        def access_token():
            return self.auth.grant_access_token()

        @self.route('/submit', methods=['POST'], endpoint='submit')
        @self.request_access_token
        @request_content_type('application/octet-stream')
        @response_content_type('text/plain')
        def submit():
            document = request.get_data()
            if not document:
                raise BadRequest()
            process_id = self.process.submit(document)
            return Response(process_id, 200, mimetype='text/plain')

        @self.route('/retrieve/<process_id>', endpoint='retrieve')
        @self.request_access_token
        @request_content_type('')
        @response_content_type('text/xml')
        def retrieve(process_id):
            result = self.process.retrieve(process_id)
            if result is None:
                raise NotFound()
            return Response(result, 200, mimetype='text/xml')
