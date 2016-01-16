__author__ = 'brayden'

from . import Base
from tornado.web import asynchronous, authenticated
from passlib.hash import sha512_crypt


class Mailboxes(Base):
    @asynchronous
    @authenticated
    def get(self):
        template = self.template_path + "/mailboxes.template"
        if self.get_argument("domain", False) and not self.get_argument("domain") == "all":
            self.render(template,
                        mailboxes=self.application.database.VirtualUsers.select().where(
                                self.application.database.VirtualUsers.domain == int(self.get_argument("domain"))).join(
                                self.application.database.VirtualDomains),
                        domains=self.application.database.VirtualDomains.select(),
                        current_domain=self.get_argument('domain'))
        else:
            self.render(template,
                        mailboxes=self.application.database.VirtualUsers.select().join(
                                self.application.database.VirtualDomains),
                        domains=self.application.database.VirtualDomains.select(), current_domain=0)

    @asynchronous
    @authenticated
    def post(self):
        template = self.template_path + "/mailboxes.template"
        if all(k in self.request.arguments for k in ("username", "password", "domain")):
            # Thanks a bajillion to ppjet6 for the passlib example, https://bitbucket.org/ppjet6/dovecot-passgen/
            rounds = 5000
            scheme_header = "{SHA512-CRYPT}"
            sha_hash = sha512_crypt.encrypt(self.get_argument("password"), rounds=rounds, implicit_rounds=True)
            self.application.database.VirtualUsers.create(domain=int(self.get_argument('domain')),
                                                          password=scheme_header + sha_hash, email=self.get_argument('username'))

        self.render(template,
                        mailboxes=self.application.database.VirtualUsers.select().join(
                                self.application.database.VirtualDomains),
                        domains=self.application.database.VirtualDomains.select(),
                        current_domain=0)