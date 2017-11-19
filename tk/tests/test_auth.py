from time import sleep
from unittest import TestCase

from tk.auth import Auth


class AuthTest(TestCase):
    def testGrantShouldProduceAccessToken(self):
        auth = Auth('foo', 9)
        self.assertRegex(auth.grant_access_token(),
                         '^[^.]+\.[^.]+\.[^.]+$')

    def testVerification(self):
        auth = Auth('foo', 9)
        self.assertTrue(auth.verify_access_token(auth.grant_access_token()))

    def testVerifyExpiredToken(self):
        auth = Auth('foo', 1)
        token = auth.grant_access_token()
        sleep(2)
        self.assertFalse(auth.verify_access_token(token))

    def testVerifyInvalidSignature(self):
        auth_a = Auth('foo', 9)
        auth_b = Auth('bar', 9)
        self.assertFalse(auth_b.verify_access_token(
            auth_a.grant_access_token()))
