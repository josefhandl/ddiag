#!venv/bin/python3

import datetime
import json
import jwt
import jwt.algorithms
import posixpath
import requests
import ssl
import sys
import warnings
from jwt import PyJWKClient, PyJWKClientError
from pygments import highlight, lexers, formatters


# Suppress urllib3 InsecureRequestWarning
warnings.filterwarnings('ignore', module='urllib3')

class JWTVerifier:
    _token = None
    _insecure = None
    _wellknown_config = None
    _token_header = None
    _token_payload = None
    _token_issuer = None
    _userinfo = None

    def __init__(self, token, insecure):
        self._token = token
        self._insecure = insecure

    def get_token_header(self):
        if not self._token_header: self._decode_token()
        return self._token_header

    def get_token_payload(self):
        if not self._token_payload: self._decode_token()
        return self._token_payload

    def get_token_issuer(self):
        if not self._token_issuer: self._decode_token()
        return self._token_issuer

    def get_wellknown_config(self):
        if not self._wellknown_config: self._obtain_wellknown_config()
        return self._wellknown_config

    def get_userinfo(self):
        if not self._userinfo: self._obtain_userinfo()
        return self._userinfo

    def _decode_token(self):
        """
        WARNING: Verify validity of given JWT token for OAuth2.
        Accepts any valid tokens from any issuer including owns!
        Expects optional JWT parameters!
        """

        token = self._token

        # Decode token (without verification) to obtain useful data
        try:
            token_header = jwt.get_unverified_header(token)
            token_payload = jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            raise Exception(f"Failed to decode token. Ex: {str(e)}")

        # Obtain desired data
        # 'sub' - user identification
        token_sub = token_payload.get('sub')
        # 'iss' - issuer of the token, required for verification
        token_iss = token_payload.get('iss')

        if not token_sub:
            raise Exception("Missing 'sub' parameter in JWT token payload.")

        if not token_iss:
            raise Exception("Missing 'iss' parameter in JWT token payload.")

        self._token_header = token_header
        self._token_payload = token_payload
        self._token_issuer = token_iss

    def _make_request(self, url, headers = None):
        try:
            response = requests.get(url, headers=headers, verify=(not self._insecure))
        except Exception as e:
            raise Exception(f"Contacting the token issuer failed. Ex: {str(e)}")

        if response.status_code != 200:
            raise Exception(f"Contacting the token issuer returns HTTP code {response.status_code}.")

        try:
            response = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise Exception("Failed to parse response from token issuer.")

        return response

    def _obtain_wellknown_config(self):
        wellknown_url = posixpath.join(self.get_token_issuer(), ".well-known/openid-configuration")
        self._wellknown_config = self._make_request(wellknown_url)

    def _obtain_userinfo(self):
        userinfo_uri = self.get_wellknown_config().get("userinfo_endpoint")
        if not userinfo_uri:
            raise Exception("Failed to obtain issuer userinfo endpoint.")
        headers = {"Authorization": f"Bearer {self._token}"}
        self._userinfo = self._make_request(userinfo_uri, headers)

    def verify_token(self):
        token = self._token
        token_iss = self.get_token_issuer()

        # Obtain issuer signing key to verify the token
        jwk_uri = self.get_wellknown_config().get('jwks_uri')
        if not jwk_uri:
            raise Exception("Failed to obtain issuer signing key endpoint.")

        # Get signing key from the "jwk_uri"
        try:
            if self._insecure:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                jwks_client = PyJWKClient(jwk_uri, ssl_context=ssl_context)
            else:
                jwks_client = PyJWKClient(jwk_uri)
            issuer_signing = jwks_client.get_signing_key_from_jwt(token).key
        except (PyJWKClientError, Exception) as e:
            raise Exception(f"Failed to obtain issuer signing key. Ex: {str(e)}")

        # Get 'alg' - used algorithm - useful, but not desired
        token_alg = self._token_header.get('alg')
        # If the token does not contain the 'alg' parameter, try list of supported algorithms by the library
        if not token_alg:
            token_alg = list(jwt.algorithms.get_default_algorithms().keys())

        # Verify the token (ignore audience)
        try:
            jwt.decode(
                token,
                key = issuer_signing,
                algorithms = token_alg,
                issuer = token_iss,
                options = {
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": False,
                    "verify_iss": True,
                }
            )
        except Exception as e:
            raise Exception(f"Failed to verify token. Ex: {str(e)}")

        return True

def print_json(raw_json):
    formatted_json = json.dumps(raw_json, sort_keys=True, indent=2)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json, end="")


def exit_with_msg():
    print(f"Usage: {sys.argv[0]} [--verify] [--userinfo] [--insecure] <jwt_token>")
    print(f"Options:")
    print(f"  --verify      Verify validity of the JWT token")
    print(f"  --userinfo    Call the OIDC userinfo endpoint")
    print(f"  --insecure    Skip TLS certificate verification when issuer contacting")
    exit(1)


if __name__ == "__main__":
    # Parse arguments - flexible order
    verify = False
    insecure = False
    userinfo = False
    token = None

    for arg in sys.argv[1:]:
        if arg == "--verify":
            verify = True
        elif arg == "--userinfo":
            userinfo = True
        elif arg == "--insecure":
            insecure = True
        elif not arg.startswith("-"):
            token = arg
        else:
            print(f"Unknown option: {arg}")
            exit_with_msg()

    if not token:
        exit_with_msg()

    if insecure:
        print("Warning: TLS certificate verification is disabled")

    jwtVerifier = JWTVerifier(token, insecure)

    # Print JWT token
    #=================================
    print("Header:")
    print("--------------------")
    print_json(jwtVerifier.get_token_header())
    print()
    print("Payload:")
    print("--------------------")
    print_json(jwtVerifier.get_token_payload())
    # Print times
    iat_unix = jwtVerifier.get_token_payload().get("iat")
    exp_unix = jwtVerifier.get_token_payload().get("exp")
    iat = datetime.datetime.fromtimestamp(int(iat_unix)).strftime('%Y-%m-%d %H:%M:%S')
    exp = datetime.datetime.fromtimestamp(int(exp_unix)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Issued at  (IAT): {iat}")
    print(f"Expiration (EXP): {exp}")
    print()

    # Verify JWT token
    #=================================
    if verify:
        print("Token validity:")
        print("--------------------")
        try:
            jwtVerifier.verify_token()
            print("Token is valid")
        except Exception as e:
            print(f"Token is NOT valid. Ex: {e}")
            exit(2)
        print()

    # Print user info
    #=================================
    if userinfo:
        print("User info:")
        print("--------------------")
        print_json(jwtVerifier.get_userinfo())
