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


class SubmitTest(IntegrationTestCase):
    @data_provider(provide_disallowed_submit_methods)
    def testWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/submit', method=method)
        self.assertEquals(405, response.status_code)

    def testWithUnsupportedMediaTypeShould415(self):
        response = self._flask_app_client.post('/submit')
        self.assertEquals(415, response.status_code)

    def testWithNotAcceptableShould406(self):
        response = self._flask_app_client.post('/submit', headers={
            'Content-Type': 'application/octet-stream'
        })
        self.assertEquals(406, response.status_code)

    def testWithMissingDocumentShould400(self):
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        })
        self.assertEquals(400, response.status_code)

    @requests_mock.mock()
    def testSuccess(self, m):
        m.post(self._flask_app.config['SOURCEBOX_URL'], text=PROFILE)
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        }, data=b'I am an excellent CV, mind you.')
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
        })
        self.assertEquals(response.status_code, 415)

    def testWithNotAcceptableShould406(self):
        response = self._flask_app_client.get('/retrieve/foo')
        self.assertEquals(response.status_code, 406)

    def testWithUnknownProcessIdShould404(self):
        response = self._flask_app_client.get('/retrieve/foo', headers={
            'Accept': 'text/xml',
        })
        self.assertEquals(response.status_code, 404)

    @requests_mock.mock()
    def testSuccessWithProcessedDocument(self, m):
        m.post(self._flask_app.config['SOURCEBOX_URL'], text=PROFILE)
        submit_response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        }, data=b'I am an excellent CV, mind you.')
        process_id = submit_response.get_data(as_text=True)
        response = self._flask_app_client.get('/retrieve/%s' % process_id,
                                              headers={
                                                  'Accept': 'text/xml',
                                              })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.get_data(as_text=True), PROFILE)
