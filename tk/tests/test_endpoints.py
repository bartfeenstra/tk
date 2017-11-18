from tk.tests import IntegrationTestCase, data_provider


def provide_disallowed_submit_methods():
    return {
        'GET': ('GET',),
        'PUT': ('PUT',),
        'PATCH': ('PATCH',),
        'DELETE': ('DELETE',),
    }


def provide_disallowed_retrieve_methods():
    return {
        'POST': ('POST',),
        'PUT': ('PUT',),
        'PATCH': ('PATCH',),
        'DELETE': ('DELETE',),
    }


class SubmitTest(IntegrationTestCase):
    @data_provider(provide_disallowed_submit_methods)
    def testSubmitWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/submit', method=method)
        self.assertEquals(405, response.status_code)

    def testSubmitWithUnsupportedMediaTypeShould415(self):
        response = self._flask_app_client.post('/submit')
        self.assertEquals(415, response.status_code)

    def testSubmitWithNotAcceptableShould406(self):
        response = self._flask_app_client.post('/submit', headers={
            'Content-Type': 'application/octet-stream'
        })
        self.assertEquals(406, response.status_code)

    def testSubmit(self):
        response = self._flask_app_client.post('/submit', headers={
            'Accept': 'text/plain',
            'Content-Type': 'application/octet-stream'
        })
        self.assertEquals(200, response.status_code)
        # Assert the response contains a plain-text process UUID.
        self.assertRegex(response.get_data(
            as_text=True), '[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


class RetrieveTest(IntegrationTestCase):
    @data_provider(provide_disallowed_retrieve_methods)
    def testRetrieveWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/retrieve/foo', method=method)
        self.assertEquals(response.status_code, 405)

    def testRetrieveWithUnsupportedMediaTypeShould415(self):
        response = self._flask_app_client.get('/retrieve/foo', headers={
            'Content-Type': 'text/plain',
        })
        self.assertEquals(response.status_code, 415)

    def testRetrieveWithNotAcceptableShould406(self):
        response = self._flask_app_client.get('/retrieve/foo')
        self.assertEquals(response.status_code, 406)

    def testRetrieveWithUnknownProcessIdShould404(self):
        response = self._flask_app_client.get('/retrieve/foo', headers={
            'Accept': 'text/xml',
        })
        self.assertEquals(response.status_code, 404)

    def testRetrieveWithUnprocessedDocument(self):
        process_id = self._flask_app.process.submit()
        response = self._flask_app_client.get('/retrieve/%s' % process_id, headers={
            'Accept': 'text/xml',
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.get_data(as_text=True), 'PROGRESS')

    def testRetrieveWithProcessedDocument(self):
        process_id = self._flask_app.process.submit()
        response = self._flask_app_client.get('/retrieve/%s' % process_id, headers={
            'Accept': 'text/xml',
        })
        self.assertEquals(response.status_code, 200)
        # @todo Confirm output.
        self.skipTest()
