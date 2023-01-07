from dotenv import load_dotenv
import os
import json
from flask import request
from functools import wraps
import jwt
from jose import jwt
from urllib.request import urlopen


# Take environment variables from ".env"
# (file should be in the root directory of your project)
load_dotenv()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
ALGORITHMS = [os.environ.get("ALGORITHMS")]

print(AUTH0_DOMAIN, API_AUDIENCE, ALGORITHMS)


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    print("get_token_auth_header")

    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {
                "code": "Missing authorization header",
                "description": "Authorization header is expected",
            },
            401,
        )

    parts = auth.split(" ")
    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must start with" " Bearer",
            },
            401,
        )
    elif len(parts) == 1:
        raise AuthError(
            {"code": "invalid_header", "description": "Token not found"}, 401
        )

    # token = parts[1].rstrip().lstrip()
    token = parts[1]
    return token


def check_permissions(permission, payload):
    print("check_permissions")
    print(permission, payload)
    if permission not in payload["permissions"]:
        raise AuthError(
            {
                "description": "User don't have sufficient permission",
                "status_code": 403,
            },
            403,
        )

    if "permissions" not in payload.keys():
        raise AuthError(
            {"description": "Permissions not included in JWT", "status_code": 400}, 400
        )

    if "permissions" not in payload:
        raise AuthError(
            {"description": "Permissions not included in JWT", "status_code": 400}, 400
        )
    return True


def verify_decode_jwt(token):
    """
    Use https://stackoverflow.com/questions/62640016/decoding-jwt-autherror
    -code-invalid-header-description-unable-to-pa
    """
    print("verify_decode_jwt")

    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())

    unverified_header = jwt.get_unverified_header(token)
    print(unverified_header)
    if "kid" not in unverified_header:
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization malformed."}, 401
        )

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token expired."}, 401
            )
        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    "code": "invalid_claims",
                    "description": "Incorrect claims. \
                    Please, check the audience and issuer.",
                },
                401,
            )
        except Exception:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token.",
                },
                400,
            )
    raise AuthError(
        {
            "code": "invalid_header",
            "description": "Unable to find the appropriate key.",
        },
        400,
    )


def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
