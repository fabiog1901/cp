"""The authentication state."""

import hashlib
import os
import random
import time

import reflex as rx

from .. import db
from .base import BaseState
from ..models import WebUser, User

PEPPER = os.getenv("PEPPER")


class AuthState(BaseState):
    """The authentication state for sign up and login page."""

    username: str
    password: str

    def login(self):
        user: User = db.get_user(self.username)

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
            self.webuser = WebUser(user.username, user.role, user.groups)

            # reset the attempts if there were any previous unsuccessful attempts to login
            if user.attempts > 0:
                db.reset_attempts(self.username)

            db.insert_event_log(self.username, "LOGIN")
            return rx.redirect(self.original_url)
        else:
            db.insert_event_log(self.username, "LOGIN FAILURE")
            db.increase_attempt(self.username)
            # mask how long it takes to come to this code path
            time.sleep(random.random() + 1)
            return rx.window_alert("Invalid username or password.")
