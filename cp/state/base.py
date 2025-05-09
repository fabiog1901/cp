from typing import Optional

import reflex as rx

from ..models import WebUser


class BaseState(rx.State):
    """The base state for the app."""

    webuser: Optional[WebUser] = None

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
