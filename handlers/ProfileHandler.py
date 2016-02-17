from . import Base
from tornado.web import asynchronous, authenticated
import os
from peewee import IntegrityError


class Profile(Base):
    @asynchronous
    @authenticated
    def get(self):
        template = os.path.join(self.template_path, "profile.template")
        self.render(template, message=None, success=None)

    @asynchronous
    @authenticated
    def post(self):
        template = os.path.join(self.template_path, "profile.template")
        if self.get_argument("action") == "update_password":
            if self.get_argument("new_password") == self.get_argument("confirm_password"):
                self.application.authentication.change_password(self.current_user, self.get_argument("new_password"))
                self.render(template, message=None, success=True)
            else:
                self.render(template, message=self.locale.translate("Passwords didn't match"), success=False)
        elif self.get_argument("action") == "update_username":
            new_username = self.get_argument("new_username")
            if len(new_username) > 128:
                self.render(template, message=self.locale.translate("New username too long"), success=None)
            else:
                try:
                    self.application.authentication.change_username(self.current_user, new_username)
                    self.set_cookie("username", new_username, path='/', expires_days=3)
                    self.current_user = new_username
                    self.render(template, message=None, success=True)
                except IntegrityError:
                    self.render(template, message=self.locale.translate("Username must be unique"), success=None)
        else:
            self.render(template, message=None, success=None)