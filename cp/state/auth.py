"""The authentication state."""

import hashlib
import os
import random
import time
from urllib.parse import urlencode

import reflex as rx
import jwt
from jwt.algorithms import RSAAlgorithm
import requests
from .. import db
from ..models import User, WebUser
from .base import BaseState

PEPPER = os.getenv("PEPPER")


def get_jwks_keys():
    jwks_url = os.getenv("SSO_JWKS_URL")
    response = requests.get(jwks_url)
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
                issuer=os.getenv("SSO_ISSUER"),
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
            os.getenv("SSO_TOKEN_URL"),
            data={
                "grant_type": "authorization_code",
                "code": self.router.page.params.get("code"),
                "redirect_uri": os.getenv("SSO_REDIRECT_URI"),
                "client_id": os.getenv("SSO_CLIENT_ID"),
                "client_secret": os.getenv("SSO_CLIENT_SECRET"),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_res.status_code == 200:
            tokens = token_res.json()
            access_token = tokens.get("access_token")

            try:
                user_claims = validate_token(
                    access_token, audience=os.getenv("SSO_CLIENT_ID")
                )
                
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
                    return rx.window_alert("User is not authorized. Contact your administrator.")

                self.webuser = WebUser(user_claims.get("preferred_username"), list(user_roles), list(user_groups))

                db.insert_event_log(
                self.webuser.username,
                    "LOGIN",
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
        query = urlencode(
            {
                "client_id": os.getenv("SSO_CLIENT_ID"),
                "redirect_uri": os.getenv("SSO_REDIRECT_URI"),
                "response_type": "code",
                "scope": "openid email profile",
            }
        )
        return rx.redirect(f"{os.getenv('SSO_AUTH_URL')}?{query}")

    def login(self):
        user: User = db.get_user(self.username)

        grp_role_maps: dict[str, list[str]] = {
            x.role: x.groups for x in db.get_role_to_groups_mappings()
        }

        if not user:
            # mask how long it takes to come to this code path
            time.sleep(random.random() + 1)
            return rx.window_alert("Invalid username or password.")

        # lock the user after 3 failed login attempts
        if user.attempts >= 3:
            # mask how long it takes to come to this code path
            time.sleep(random.random() + 1)
            return rx.window_alert("User is locked. Contact your administrator.")

        # Recompute hash from user entered password
        password_hash = hashlib.pbkdf2_hmac(
            user.hash_algo,
            self.password.encode("utf-8") + PEPPER.encode("utf-8"),
            user.salt,
            user.iterations,
        )

        if password_hash == user.password_hash:
            # create a WebUser out of the User
            # assign all roles and groups
            user_roles = set[str]()
            user_groups = set[str]()
            for r in ["ro", "rw", "admin"]:
                for g in grp_role_maps.get(r):
                    if g in user.groups:
                        user_roles.add(r)
                        user_groups.add(g)

            self.webuser = WebUser(user.username, list(user_roles), list(user_groups))

            # reset the attempts if there were any previous unsuccessful attempts to login
            if user.attempts > 0:
                db.reset_attempts(self.webuser.username)

            db.insert_event_log(
                self.webuser.username,
                "LOGIN",
                {
                    "roles": list(self.webuser.roles),
                    "groups": list(self.webuser.groups),
                },
            )
            return rx.redirect(self.original_url)
        else:
            db.insert_event_log(self.username, "LOGIN FAILURE")
            db.increase_attempt(self.username)
            # mask how long it takes to come to this code path
            time.sleep(random.random() + 1)
            return rx.window_alert("Invalid username or password.")
