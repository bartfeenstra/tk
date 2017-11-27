import base64
from time import sleep

import requests_mock

from tk.tests import IntegrationTestCase, data_provider

PROFILE = """
<?xml version="1.0" encoding="UTF-8" ?>
<Profile>
  <FirstName>Taalbeheersing</FirstName>
    <LastName>van de Petra Paula Maria</LastName>
    <Address>
        <StreetName>Hoofdstraat</StreetName>
        <StreetNumberBase>15-A</StreetNumberBase>
        <PostalCode>6717 AA</PostalCode>
        <City>EDE</City>
    </Address>
</Profile>
"""


def delayed_profile(*_):
    """
    Returns a document profile after a delay.
    :return: The profile.
    """
    sleep(5)
    return PROFILE


def provide_disallowed_submit_methods():
    """
    Returns the HTTP methods disallowed by the /submit endpoint.
    See data_provider().
    """
    return {
        'GET': ('GET',),
        'PUT': ('PUT',),
        'PATCH': ('PATCH',),
        'DELETE': ('DELETE',),
    }


def provide_disallowed_retrieve_methods():
    """
    Returns the HTTP methods disallowed by the /retrieve/{} endpoint.
    See data_provider().
    """
    return {
        'POST': ('POST',),
        'PUT': ('PUT',),
        'PATCH': ('PATCH',),
        'DELETE': ('DELETE',),
    }


def provide_disallowed_access_token_methods():
    """
    Returns the HTTP methods disallowed by the /accesstoken/{} endpoint.
    See data_provider().
    """
    return {
        'POST': ('POST',),
        'PUT': ('PUT',),
        'PATCH': ('PATCH',),
        'DELETE': ('DELETE',),
    }


def provide_4xx_codes():
    """
    Returns the HTTP 4xx codes.
    See data_provider().
    """
    codes = list(range(400, 418)) + list(range(421, 424)) + [426, 428, 429, 431, 451]
    data = {}
    for code in codes:
        data[code] = (code,)
    return data


def provide_5xx_codes():
    """
    Returns the HTTP 5xx codes.
    See data_provider().
    """
    codes = list(range(500, 508)) + [510, 511]
    data = {}
    for code in codes:
        data[code] = (code,)
    return data


class AccessTokenTest(IntegrationTestCase):
    def setUp(self):
        super().setUp()
        self._user_name = 'My name is Bart'
        self._password = '(32jbfmIu092%njF'
        self._flask_app.add_user(self._user_name, self._password)

    def build_basic_auth_headers(self, name, password):
        credentials = '%s:%s' % (name, password)
        return {
            'Authorization': 'Basic %s' % base64.b64encode(bytes(credentials, 'utf-8')).decode('latin1'),
        }

    @data_provider(provide_disallowed_access_token_methods)
    def testWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/accesstoken', method=method)
        self.assertEquals(405, response.status_code)

    def testWithUnsupportedMediaTypeShould415(self):
        headers = self.build_basic_auth_headers(
            self._user_name, self._password)
        headers['Content-Type'] = 'text/plain'
        response = self._flask_app_client.get('/accesstoken', headers=headers)
        self.assertEquals(415, response.status_code)

    def testWithNotAcceptableShould406(self):
        headers = self.build_basic_auth_headers(
            self._user_name, self._password)
        headers['Accept'] = 'application/json'
        response = self._flask_app_client.get('/accesstoken', headers=headers)
        self.assertEquals(406, response.status_code)

    def testWithMissingAuthorizationShould401(self):
        response = self._flask_app_client.get('/accesstoken', headers={
            'Accept': 'text/plain',
        })
        self.assertEquals(401, response.status_code)
        self.assertIn('WWW-Authenticate', response.headers)

    def testWithForbiddenShould403(self):
        headers = self.build_basic_auth_headers('for', 'bidden')
        headers['Accept'] = 'text/plain'
        response = self._flask_app_client.get('/accesstoken', headers=headers)
        # @todo Assert for a 403 error. However, Flask-HTTPAuth, the library we
        #  use for HTTP Basic Authentication, does not distinguish between 401
        #  and 403, and returns 401 regardless.
        self.assertEquals(401, response.status_code)

    def testSuccess(self):
        headers = self.build_basic_auth_headers(
            self._user_name, self._password)
        headers['Accept'] = 'text/plain'
        response = self._flask_app_client.get('/accesstoken', headers=headers)
        self.assertEquals(200, response.status_code)
        # Assert the response contains a plain-text JSON Web Token.
        self.assertRegex(response.get_data(
            as_text=True),
            '^[^.]+\.[^.]+\.[^.]+$')


class SubmitTest(IntegrationTestCase):
    @data_provider(provide_disallowed_submit_methods)
    def testWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/submit', method=method)
        self.assertEquals(405, response.status_code)

    def testWithUnsupportedMediaTypeShould415(self):
        response = self._flask_app_client.post('/submit', query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(415, response.status_code)

    def testWithNotAcceptableShould406(self):
        response = self._flask_app_client.post('/submit', headers={
            'Content-Type': 'application/octet-stream'
        }, query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(406, response.status_code)

    def testWithMissingDocumentShould400(self):
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        }, query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(400, response.status_code)

    def testWithMissingAuthorizationShould401(self):
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        })
        self.assertEquals(401, response.status_code)

    def testWithForbiddenShould403(self):
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        }, query_string={
            'access_token': 'foo.bar.baz',
        })
        self.assertEquals(403, response.status_code)

    @requests_mock.mock()
    def testSuccess(self, m):
        m.post(self._flask_app.config['SOURCEBOX_URL'], text=delayed_profile)
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        }, data=b'I am an excellent CV, mind you.', query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(200, response.status_code)
        # Assert the response contains a plain-text process UUID.
        self.assertRegex(response.get_data(
            as_text=True),
            '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


class RetrieveTest(IntegrationTestCase):
    @data_provider(provide_disallowed_retrieve_methods)
    def testWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/retrieve/foo', method=method)
        self.assertEquals(response.status_code, 405)

    def testWithUnsupportedMediaTypeShould415(self):
        response = self._flask_app_client.get('/retrieve/foo', headers={
            'Content-Type': 'text/plain',
        }, query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(response.status_code, 415)

    def testWithNotAcceptableShould406(self):
        response = self._flask_app_client.get('/retrieve/foo', query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(response.status_code, 406)

    def testWithUnknownProcessIdShould404(self):
        response = self._flask_app_client.get('/retrieve/foo', headers={
            'Accept': 'text/xml',
        }, query_string={
            'access_token': self._flask_app.auth.grant_access_token('User Foo'),
        })
        self.assertEquals(response.status_code, 404)

    def testWithMissingAuthorizationShould401(self):
        response = self._flask_app_client.get('/retrieve/foo',
                                              headers={
                                                  'Accept': 'text/xml',
                                              })
        self.assertEquals(response.status_code, 401)
        self.assertEquals(401, response.status_code)

    def testWithForbiddenShould403(self):
        response = self._flask_app_client.get('/retrieve/foo',
                                              headers={
                                                  'Accept': 'text/xml',
                                              }, query_string={
                                                  'access_token': 'foo.bar.baz',
                                              })
        self.assertEquals(403, response.status_code)

    @requests_mock.mock()
    def testSuccessWithUnprocessedDocument(self, m):
        user_name = 'User Foo'
        m.post(self._flask_app.config['SOURCEBOX_URL'], text=delayed_profile)
        process_id = self._flask_app.process.submit(
            user_name, b'I am an excellent CV, mind you.')
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers={
                                                  'Accept': 'text/xml',
                                              }, query_string={
                                                  'access_token': self._flask_app.auth.grant_access_token(user_name),
                                              })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.get_data(as_text=True), 'PROGRESS')

    @requests_mock.mock()
    def testSuccessWithProcessedDocument(self, m):
        user_name = 'User Foo'
        m.post(self._flask_app.config['SOURCEBOX_URL'], text=PROFILE)
        process_id = self._flask_app.process.submit(
            user_name, b'I am an excellent CV too, mind you.')
        # Sleep to allow asynchronous processing of the document. This is not
        #  ideal as it could lead to random test failures, but it is
        #  unavoidable without additional tools.
        sleep(6)
        headers = {
            'Accept': 'text/xml',
        }
        query = {
            'access_token': self._flask_app.auth.grant_access_token(user_name),
        }
        response = self._flask_app_client.get('/retrieve/%s' % process_id, headers=headers, query_string=query)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.get_data(as_text=True), PROFILE)

        # Confirm the results are no longer available, in order to keep memory consumption reasonable.
        response = self._flask_app_client.get('/retrieve/%s' % process_id, headers=headers, query_string=query)
        self.assertEquals(response.status_code, 404)

    @requests_mock.mock()
    def testSuccessWithSomeoneElsesDocument(self, m):
        my_user_name = 'User Foo'
        someone_elses_user_name = 'User Bar'
        m.post(self._flask_app.config['SOURCEBOX_URL'], text=delayed_profile)
        process_id = self._flask_app.process.submit(
            someone_elses_user_name, b'I am an excellent CV, mind you.')
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers={
                                                  'Accept': 'text/xml',
                                              }, query_string={
                                                  'access_token': self._flask_app.auth.grant_access_token(my_user_name),
                                              })
        self.assertEquals(response.status_code, 403)

    @requests_mock.mock()
    @data_provider(provide_4xx_codes)
    def testWithUpstream4xxResponse(self, m, upstream_status_code):
        m.post(self._flask_app.config['SOURCEBOX_URL'], status_code=upstream_status_code)
        user_name = 'User Foo'
        process_id = self._flask_app.process.submit(user_name, b'Something is wrong with me.')
        # Sleep to allow asynchronous processing of the document. This is not
        #  ideal as it could lead to random test failures, but it is
        #  unavoidable without additional tools.
        sleep(2)
        headers = {
            'Accept': 'text/xml',
        }
        query = {
            'access_token': self._flask_app.auth.grant_access_token(user_name),
        }
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers=headers, query_string=query)
        self.assertEquals(response.status_code, 500)

        # Confirm the results are no longer available, in order to keep memory consumption reasonable.
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers=headers, query_string=query)
        self.assertEquals(response.status_code, 404)

    @requests_mock.mock()
    @data_provider(provide_5xx_codes)
    def testWithUpstream5xxResponse(self, m, upstream_status_code):
        m.post(self._flask_app.config['SOURCEBOX_URL'], status_code=upstream_status_code)
        user_name = 'User Foo'
        process_id = self._flask_app.process.submit(user_name, b'I might just crash you.')
        # Sleep to allow asynchronous processing of the document. This is not
        #  ideal as it could lead to random test failures, but it is
        #  unavoidable without additional tools.
        sleep(2)
        headers = {
            'Accept': 'text/xml',
        }
        query = {
            'access_token': self._flask_app.auth.grant_access_token(user_name),
        }
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers=headers, query_string=query)
        self.assertEquals(response.status_code, 502)

        # Confirm the results are no longer available, in order to keep memory consumption reasonable.
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers=headers, query_string=query)
        self.assertEquals(response.status_code, 404)
