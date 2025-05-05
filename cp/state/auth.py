"""The authentication state."""

import hashlib
import os

import reflex as rx

from .. import db
from .base import BaseState, User

PEPPER = os.getenv("PEPPER")


class AuthState(BaseState):
    """The authentication state for sign up and login page."""

    username: str
    password: str

    def login(self):
        user = db.get_user(self.username)
        print(user)

        if not user:
            return rx.window_alert("Invalid username or password.")

        if user.attempts >= 3:
            return rx.window_alert("User is locked. Contact your administrator.")

        # Recompute hash from user entered password
        password_hash = hashlib.pbkdf2_hmac(
            user.hash_algo,
            self.password.encode("utf-8") + PEPPER.encode("utf-8"),
            user.salt,
            user.iterations,
        )

        if password_hash == user.password_hash:
            self.user = user
            if user.attempts > 0:
                db.reset_attempts(self.username)
            return rx.redirect("/")
        else:
            db.increase_attempt(self.username)
            return rx.window_alert("Invalid username or password.")
