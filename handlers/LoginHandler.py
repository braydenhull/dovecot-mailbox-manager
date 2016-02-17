__author__ = 'brayden'

from . import Base
from tornado.web import asynchronous
from urllib.parse import urlparse
import os


class Login(Base):
    @asynchronous
    def get(self):
        template = os.path.join(self.template_path, "login.template")
        self.render(template, message=None, username=None)

    @asynchronous
    def post(self):
        template = os.path.join(self.template_path, "login.template")
        if all(k in self.request.arguments for k in ("username", "password")):
            try:
                if self.application.authentication.check_credentials(self.get_argument('username'), self.get_argument('password')):
                    self.set_cookie('session', self.application.authentication.create_session(self.get_argument('username'), self.request.remote_ip), path='/', expires_days=3)
                    self.set_cookie('username', self.get_argument('username'), path='/', expires_days=3)
                    self.redirect(urlparse(self.get_argument('next', '/')).path) # Using urlparse will strip off domains so they can't do redirects to other websites
                else:
                    self.render(template, message=self.locale.translate("Incorrect username or password"), username=self.get_argument('username'))
            except self.application.authentication.BadUser:
                self.render(template, message=self.locale.translate("Incorrect username or password"), username=self.get_argument('username'))
        else:
            self.render(template, message=self.locale.translate("Please include all necessary parameters"), username=None)


class Logout(Base):
    @asynchronous
    def get(self):
        if 'session' in self.request.cookies:
            self.application.authentication.remove_session(self.get_cookie('session'))

        self.redirect(self.application.settings['login_url'])