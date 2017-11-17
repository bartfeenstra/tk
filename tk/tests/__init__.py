from unittest import TestCase

from tk.flask.app import App


def data_provider(data_provider):
    def decorator(test_method):
        def multiplier(self, *test_method_args, **test_method_kwargs):
            """
            The replacement (decorated) test method.
            :param self:
            :param args:
            :return:
            """
            for fixture_name, test_method_fixture_args in data_provider().items():
                try:
                    test_method(self, *test_method_args,
                                *test_method_fixture_args,
                                **test_method_kwargs)
                except AssertionError:
                    raise AssertionError(
                        'Assertion failed with data set "%s"' % str(fixture_name))
                except Exception:
                    raise AssertionError(
                        'Unexpected error with data set "%s"' % str(
                            fixture_name))

        return multiplier

    return decorator


class IntegrationTestCase(TestCase):
    def setUp(self):
        self._flask_app = App()
        self._flask_app.config.update(SERVER_NAME='example.com')
        self._flask_app_context = self._flask_app.app_context()
        self._flask_app_context.push()
        self._flask_app_client = self._flask_app.test_client()

    def tearDown(self):
        self._flask_app_context.pop()
