import datetime

import jwcrypto.jwk as jwk
import python_jwt as jwt


class Auth:
    def __init__(self, secret_key, ttl):
        assert secret_key is not None
        jwt_key = jwk.JWK.generate(kty='oct', k=secret_key)
        # A little assurance that we will always enforce a secure signature. If
        # the key is None, the JWT signature algorithm will be None, leading to
        # unsigned and therefore unauthenticated tokens. For more details, see
        # https://www.chosenplaintext.ca/2015/03/31/jwt-algorithm-confusion.html.
        assert jwt_key is not None
        self._jwt_key = jwt_key
        self._algorithm = 'HS512'
        self._ttl = ttl

    def grant_access_token(self):
        return jwt.generate_jwt({}, self._jwt_key, self._algorithm,
                                datetime.timedelta(seconds=self._ttl))

    def verify_access_token(self, access_token):
        try:
            jwt.verify_jwt(access_token, self._jwt_key,
                           [self._algorithm])
        # This is an overly broad exception clause, because:
        # 1) the JWT library does not raise exceptions of a single type.
        # 2) calling code will convert this to an appropriate HTTP response.
        except Exception as e:
            return False

        return True
