from functools import wraps
from unittest import TestCase

import requests
import requests_mock

from tk.flask.app import App


def data_provider(data_provider):
    """
    Provides a test method with test data.

    Applying this decorator to a test method causes that method to be run as
    many times as the data provider callable returns dictionary items.
    Failed assertions will include information about which data set failed.

    :param data_provider: A callable that generates the test data as a
      dictionary of tuples containing the test method arguments, keyed by data
      set name.
    :return:
    """
    def decorator(test_method):
        """
        The actual decorator.
        :param test_method: The test method to decorate.
        :return:
        """
        @wraps(test_method)
        def multiplier(self, *test_method_args, **test_method_kwargs):
            """
            The replacement (decorated) test method.
            :param self:
            :param test_method_args: The arguments to the decorated test
             method.
            :param test_method_kwargs: The keyword arguments to the decorated
             test method.
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


def expand_data(values):
    """
    Expands a data set.
    :param data: An iterable of scalars.
    :return:
    """
    data = {}
    for value in values:
        data[value] = (value,)
    return data


class IntegrationTestCase(TestCase):
    """
    Provides scaffolding for light-weight integration tests.
    """

    def setUp(self):
        self._flask_app = App()
        self._flask_app.config.update(SERVER_NAME='example.com')
        self._flask_app_context = self._flask_app.app_context()
        self._flask_app_context.push()
        self._flask_app_client = self._flask_app.test_client()

        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount('mock', adapter)

    def tearDown(self):
        self._flask_app_context.pop()
