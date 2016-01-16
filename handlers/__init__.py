__author__ = 'brayden'

import tornado.web
from tornado.web import HTTPError
from peewee import DoesNotExist
import tornado.locale


class Base(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        if 'title' in kwargs:
            self.title = kwargs['title']
        else:
            self.title = None

        self.template_path = self.get_template_path()

    def get_user_locale(self):
        language = self.get_cookie("language", False)
        if language:
            if language in tornado.locale.get_supported_locales():
                return tornado.locale.get(language)
            else: return None
        else: return None



    def get_template_namespace(self):
        ns = super(Base, self).get_template_namespace()

        ns.update({
            'project_name': "Dovecot Mailbox Manager",
            'database': self.application.database,
            'title': self.title,
            'authenticated': False if not self.current_user else True
        })
        return ns

    def get_current_user(self):
        if 'session' in self.request.cookies and 'username' in self.request.cookies:
            username = self.get_cookie("username")
            session = self.get_cookie("session")
            try:
                if self.application.authentication.check_session(username, session):
                    return username
            except DoesNotExist:
                return None
        return None