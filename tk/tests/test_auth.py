from time import sleep
from unittest import TestCase

from tk.auth import Auth


class AuthTest(TestCase):
    def testGrantShouldProduceAccessToken(self):
        auth = Auth('foo', 9)
        user_name = 'User Foo'
        self.assertRegex(auth.grant_access_token(user_name),
                         '^[^.]+\.[^.]+\.[^.]+$')

    def testVerification(self):
        auth = Auth('foo', 9)
        user_name = 'User Foo'
        self.assertEqual(auth.verify_access_token(
            auth.grant_access_token(user_name)), user_name)

    def testVerifyExpiredToken(self):
        auth = Auth('foo', 1)
        user_name = 'User Foo'
        token = auth.grant_access_token(user_name)
        sleep(2)
        self.assertIsNone(auth.verify_access_token(token))

    def testVerifyInvalidSignature(self):
        auth_a = Auth('foo', 9)
        auth_b = Auth('bar', 9)
        user_name = 'User Foo'
        self.assertIsNone(auth_b.verify_access_token(
            auth_a.grant_access_token(user_name)))
