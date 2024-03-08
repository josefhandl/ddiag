#!/usr/bin/python3

import requests
import posixpath
import jwt
import jwt.algorithms
from jwt import PyJWKClient, PyJWKClientError


def verify_token(token, verify = True):
    """
    WARNING: Verify validity of given JWT token for OAuth2.
    Accepts any valid tokens from any issuer including owns!
    Expects optional JWT parameters!
    """

    # Decode without verification to obtain usefull data
    #=====================================================

    try:
        token_header = jwt.get_unverified_header(token)
        token_payload = jwt.decode(token, options={"verify_signature": False})
        print(token_payload)
    except Exception as e:
        raise Exception(f"Failed to decode token. Ex: {str(e)}")

    # Obtain desired data
    #======================

    # 'sub' - user identification
    token_sub = token_payload.get('sub')
    # 'alg' - used algorithm - not desired
    token_alg = token_header.get('alg')
    # 'iss' - issuer of the token, required for verification
    token_iss = token_payload.get('iss')

    if not token_sub:
        raise Exception("Missing 'sub' parameter in JWT token payload.")

    if not token_iss:
        raise Exception("Missing 'iss' parameter in JWT token payload.")

    if verify == False:
        return False

    # Obtain issuer signing key to verify the token
    #================================================

    # Get "jwk_uri" endpoint
    issuer_wk_config_url = posixpath.join(token_iss, ".well-known/openid-configuration")
    try:
        response = requests.get(issuer_wk_config_url)
    except Exception as e:
        raise Exception("Contacting the token issuer failed.")

    if response.status_code != 200:
        raise Exception(f"Contacting the token issuer returns HTTP code {response.status_code}.")

    try:
        issuer_wk_config_data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        raise Exception("Failed to parse response from token issuer.")

    issuer_jwk_uri = issuer_wk_config_data.get('jwks_uri')
    if not issuer_jwk_uri:
        raise Exception("Failed to obtain issuer signing key.")

    # Get signing key from the "jwk_uri"
    try:
        jwks_client = PyJWKClient(issuer_jwk_uri)
        issuer_signing = jwks_client.get_signing_key_from_jwt(token).key
    except (PyJWKClientError, Exception) as e:
        raise Exception(f"Failed to obtain issuer signing key. Ex: {str(e)}")

    # If the token does not contain the 'alg' parameter, try list of supported algorithms by the library
    if not token_alg:
        token_alg = list(jwt.algorithms.get_default_algorithms().keys())

    # Verify the token
    #===================

    # (ignore audience)
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

    return True #token_sub

if __name__ == "__main__":
    token = ""
    try:
        if verify_token(token, verify=False):
            print("Info: Token is valid")
        else:
            print("Info: Token verification was skipped.")
    except Exception as e:
        print(f"Error: {str(e)}")
