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


class StaticEndpointRepositoryTest(IntegrationTestCase):
    @data_provider(provide_disallowed_submit_methods)
    def testSubmitWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/submit', method=method)
        self.assertEquals(405, response.status_code)

    @data_provider(provide_disallowed_retrieve_methods)
    def testRetrieveWithDisallowedMethodShould405(self, method):
        response = self._flask_app_client.open('/retrieve/foo', method=method)
        self.assertEquals(405, response.status_code)
