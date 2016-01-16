__author__ = 'brayden'

from tornado.ioloop import IOLoop
import tornado.web
import os
from tornado.web import url
import tornado.locale
import logging
import sys

try:
    from settings import Settings
except ImportError:
    logging.error("settings.py isn't present, remember to rename settings.py.editme to settings.py after filling in the fields")
    sys.exit(1)

from database import Database
from authentication import Authentication
import tornado.ioloop
from handlers.LoginHandler import *
from handlers.MailboxHandler import *
from handlers.DomainHandler import *
from handlers.LocaleHandler import *
from handlers.AliasHandler import *


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            autoreload=False,
            compiled_template_cache=False,
            static_hash_cache=False,
            serve_traceback=True,
            gzip=True,
            template_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')),
            static_path=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static')),
            login_url='/login'
        )

        handlers = [
            url(r'/', Domains, name="Domains", kwargs={'title': 'Domains'}),
            url('/mailboxes', Mailboxes, name="Mailboxes", kwargs={'title': 'Mailboxes'}),
            url('/login', Login, name="Login", kwargs={'title': "Login"}),
            url('/logout', Logout, name="Logout"),
            url('/set_language', SetLanguage, name="SetLanguage"),
            url('/aliases', Aliases, name="Aliases", kwargs={'title': 'Aliases'}),
        ]


        self.logger = logging.getLogger("application")
        logging.basicConfig(level=logging.DEBUG)
        self.app_settings = Settings
        self.database = Database(self.app_settings.Database.DatabaseName, {'user': self.app_settings.Database.Username,
                                                                           'passwd': self.app_settings.Database.Password,
                                                                           'host': self.app_settings.Database.Address,
                                                                           'port': self.app_settings.Database.Port})
        self.authentication = Authentication(self)

        tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), Settings.Language.TranslationFolder))
        tornado.locale.set_default_locale(Settings.Language.DefaultLanguage)

        if not self.database.is_populated():
            self.database.initialise()
            self.authentication.create_user("admin", "admin")

        tornado.web.Application.__init__(self, handlers, **settings)


application = Application()
application.listen(port=Settings.WebServer.Port, address=Settings.WebServer.Address)
tornado.ioloop.PeriodicCallback(application.database.ping, 300000).start()
IOLoop.instance().start()