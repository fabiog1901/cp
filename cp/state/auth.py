"""The authentication state."""

import time
from urllib.parse import urlencode

import jwt
import reflex as rx
import requests
from jwt.algorithms import RSAAlgorithm

from .. import db
from ..models import EventType, WebUser
from .base import BaseState

SSO_CACHE_VALID_UNTIL = 0

SSO_CLIENT_ID = ""
SSO_CLIENT_SECRET = ""
SSO_AUTH_URL = ""
SSO_TOKEN_URL = ""
SSO_USERINFO_URL = ""
SSO_REDIRECT_URI = ""
SSO_JWKS_URL = ""
SSO_ISSUER = ""


def refresh_cache():
    global SSO_CACHE_VALID_UNTIL

    global SSO_CLIENT_ID
    global SSO_CLIENT_SECRET
    global SSO_AUTH_URL
    global SSO_TOKEN_URL
    global SSO_USERINFO_URL
    global SSO_REDIRECT_URI
    global SSO_JWKS_URL
    global SSO_ISSUER
    global SSO_CLAIM_NAME

    SSO_CLIENT_ID = db.get_setting("sso_client_id")
    SSO_CLIENT_SECRET = db.get_setting("sso_client_secret")
    SSO_AUTH_URL = db.get_setting("sso_auth_url")
    SSO_TOKEN_URL = db.get_setting("sso_token_url")
    SSO_USERINFO_URL = db.get_setting("sso_userinfo_url")
    SSO_REDIRECT_URI = db.get_setting("sso_redirect_uri")
    SSO_JWKS_URL = db.get_setting("sso_jwks_url")
    SSO_ISSUER = db.get_setting("sso_issuer")
    SSO_CLAIM_NAME = db.get_setting("sso_claim_name")

    SSO_CACHE_VALID_UNTIL = time.time() + int(db.get_setting("sso_cache_expiry"))


def get_jwks_keys():
    response = requests.get(SSO_JWKS_URL)
    response.raise_for_status()
    return response.json()["keys"]


def validate_token(token: str, audience: str = None) -> dict:
    keys = get_jwks_keys()
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    for key in keys:
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
            public_key = RSAAlgorithm.from_jwk(rsa_key)
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[
                    unverified_header["alg"],
                ],
                issuer=SSO_ISSUER,
                options=dict(
                    verify_aud=False,
                    verify_sub=False,
                    verify_exp=True,
                ),
            )

        except jwt.ExpiredSignatureError:
            raise "token is expired"

        except Exception as e:
            raise f"Unable to parse authentication token: {e.args}"

    if not payload:
        raise "Invalid authorization token"

    return payload


class AuthState(BaseState):
    """The authentication state for sign up and login page."""

    username: str
    password: str

    def callback(self):
        token_res = requests.post(
            SSO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": self.router.page.params.get("code"),
                "redirect_uri": SSO_REDIRECT_URI,
                "client_id": SSO_CLIENT_ID,
                "client_secret": SSO_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_res.status_code == 200:
            tokens = token_res.json()
            access_token = tokens.get("access_token")

            try:
                user_claims = validate_token(access_token, audience=SSO_CLIENT_ID)

                grp_role_maps: dict[str, list[str]] = {
                    x.role: x.groups for x in db.get_role_to_groups_mappings()
                }

                # create a WebUser out of the User
                # assign all roles and groups
                user_roles = set[str]()
                user_groups = set[str]()
                for r in ["ro", "rw", "admin"]:
                    for g in grp_role_maps.get(r):
                        if g in user_claims.get("groups"):
                            user_roles.add(r)
                            user_groups.add(g)

                if not user_roles:
                    return rx.window_alert(
                        "User is not authorized. Contact your administrator."
                    )

                self.webuser = WebUser(
                    username=user_claims.get(SSO_CLAIM_NAME),
                    roles=list(user_roles),
                    groups=list(user_groups),
                )

                db.insert_event_log(
                    self.webuser.username,
                    EventType.LOGIN,
                    {
                        "roles": list(self.webuser.roles),
                        "groups": list(self.webuser.groups),
                    },
                )

                return rx.redirect(self.original_url)
            except Exception as e:
                print(f"Token validation failed: {e}")
                return rx.redirect("/login")

        return rx.redirect("/login")

    def login_redirect(self):
        if time.time() > SSO_CACHE_VALID_UNTIL:
            refresh_cache()

        query = urlencode(
            {
                "client_id": SSO_CLIENT_ID,
                "redirect_uri": SSO_REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
            }
        )
        return rx.redirect(f"{SSO_AUTH_URL}?{query}")
