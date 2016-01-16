__author__ = 'brayden'

from . import Base
from tornado.web import asynchronous, authenticated


class Domains(Base):
    @asynchronous
    @authenticated
    def get(self):
        template = self.template_path + "/domains.template"
        self.render(template,
                    domains=self.application.database.VirtualDomains.select())

    @asynchronous
    @authenticated
    def post(self):
        template = self.template_path + "/domains.template"
        if self.get_argument('domain', False):
            self.application.database.VirtualDomains.create(name=self.get_argument('domain'))

        self.render(template,
                    domains=self.application.database.VirtualDomains.select())
