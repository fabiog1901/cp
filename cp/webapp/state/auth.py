import logging
import time
from typing import Optional
from urllib.parse import urlencode

import jwt
import reflex as rx
import requests
from jwt.algorithms import RSAAlgorithm

from ...models import WebUser
from ...services import auth_service, settings_service

SSO_CACHE_VALID_UNTIL = 0

SSO_CLIENT_ID = ""
SSO_CLIENT_SECRET = ""
SSO_AUTH_URL = ""
SSO_TOKEN_URL = ""
SSO_USERINFO_URL = ""
SSO_REDIRECT_URI = ""
SSO_JWKS_URL = ""
SSO_ISSUER = ""
SSO_CLAIM_NAME = ""

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Raised when authentication cannot be completed safely."""


class AuthState(rx.State):
    """The authentication state for login page."""

    # protecting the webuser using Backend-Only var
    # backend-only vars start with underscore
    # https://reflex.dev/docs/vars/base-vars/#backend-only-vars

    _webuser: Optional[WebUser] = None

    @rx.var
    def webuser(self) -> WebUser | None:
        return self._webuser

    original_url: str = "/"

    @rx.event()
    async def just_return(self):
        return

    @rx.var
    def is_admin_or_rw(self) -> bool:
        if self.webuser is not None:
            return ("admin" in self.webuser.roles) or ("rw" in self.webuser.roles)
        return False

    @rx.var
    def is_admin(self) -> bool:
        if self.webuser is not None:
            return "admin" in self.webuser.roles
        return False

    def logout(self):
        """Log out a user."""
        self.reset()
        return rx.redirect("/")

    def check_login(self):
        self.original_url = self.router.page.raw_path
        if not self.is_logged_in:
            return rx.redirect("/login")

    @rx.var
    def is_logged_in(self) -> bool:
        """Check if a user is logged in."""
        return self.webuser is not None

    def callback(self):
        try:
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
                timeout=10,
            )
            token_res.raise_for_status()

            tokens = token_res.json()
            access_token = tokens.get("access_token")
            user_claims = validate_token(access_token) #, audience=SSO_CLIENT_ID)

            grp_role_maps: dict[str, list[str]] = {
                x.role: x.groups for x in auth_service.list_role_group_mappings()
            }

            user_roles = set[str]()
            user_groups = set[str]()
            claim_groups = user_claims.get("groups") or []
            for r in ["ro", "rw", "admin"]:
                for g in grp_role_maps.get(r, []):
                    if g in claim_groups:
                        user_roles.add(r)
                        user_groups.add(g)

            if not user_roles:
                return rx.window_alert(
                    "User is not authorized. Contact your administrator."
                )

            username = user_claims.get(SSO_CLAIM_NAME)
            if not username:
                raise AuthError(f"Token is missing required claim '{SSO_CLAIM_NAME}'")

            self._webuser = WebUser(
                username=username,
                roles=list(user_roles),
                groups=list(user_groups),
            )

            auth_service.record_login(
                self.webuser.username,
                list(self.webuser.roles),
                list(self.webuser.groups),
            )

            return rx.redirect(self.original_url)
        except (AuthError, requests.RequestException, ValueError) as err:
            logger.warning("Authentication callback failed: %s", err)
            return rx.redirect("/login")
        except Exception:
            logger.exception("Unexpected error during authentication callback")
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

    SSO_CLIENT_ID = settings_service.get_setting("sso_client_id")
    SSO_CLIENT_SECRET = settings_service.get_setting("sso_client_secret")
    SSO_AUTH_URL = settings_service.get_setting("sso_auth_url")
    SSO_TOKEN_URL = settings_service.get_setting("sso_token_url")
    SSO_USERINFO_URL = settings_service.get_setting("sso_userinfo_url")
    SSO_REDIRECT_URI = settings_service.get_setting("sso_redirect_uri")
    SSO_JWKS_URL = settings_service.get_setting("sso_jwks_url")
    SSO_ISSUER = settings_service.get_setting("sso_issuer")
    SSO_CLAIM_NAME = settings_service.get_setting("sso_claim_name")

    SSO_CACHE_VALID_UNTIL = time.time() + int(
        settings_service.get_setting("sso_cache_expiry")
    )


def get_jwks_keys():
    if not SSO_JWKS_URL:
        raise AuthError("SSO JWKS URL is not configured")

    try:
        response = requests.get(SSO_JWKS_URL, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as err:
        raise AuthError(f"Unable to fetch JWKS keys: {err}") from err
    except ValueError as err:
        raise AuthError("JWKS response is not valid JSON") from err

    keys = payload.get("keys")
    if not isinstance(keys, list):
        raise AuthError("JWKS response does not contain a 'keys' list")
    return keys


def validate_token(token: str, audience: str = None) -> dict:
    print(token)
    if not token:
        raise AuthError("Authorization token is missing")

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

    if not rsa_key:
        raise AuthError("No matching signing key found for authorization token")

    try:
        
        public_key = RSAAlgorithm.from_jwk(rsa_key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[unverified_header["alg"]],
            issuer=SSO_ISSUER,
            audience=audience,
            options=dict(
                verify_aud=audience is not None,
                verify_sub=False,
                verify_exp=True,
            ),
        )
    except jwt.ExpiredSignatureError as err:
        raise AuthError("Authorization token is expired") from err
    except jwt.InvalidTokenError as err:
        raise AuthError(f"Invalid authorization token: {err}") from err
    except Exception as err:
        raise AuthError(f"Unable to parse authentication token: {err}") from err

    if not payload:
        raise AuthError("Invalid authorization token")

    return payload
