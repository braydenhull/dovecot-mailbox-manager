from . import Base
from tornado.web import asynchronous
import tornado.locale


class SetLanguage(Base):
    @asynchronous
    def get(self):
        language = self.get_argument('language', False)
        if language:
            if language in tornado.locale.get_supported_locales():
                self.set_cookie('language', language)

        self.redirect(self.request.headers.get('Referer', '/'))