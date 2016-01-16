from . import Base
from tornado.web import asynchronous, authenticated


class Aliases(Base):
    @asynchronous
    @authenticated
    def get(self):
        template = self.template_path + "/aliases.template"
        if self.get_argument("domain", False) and not self.get_argument("domain") == "all":
            self.render(template,
                aliases=self.application.database.VirtualAliases.select().where(self.application.database.VirtualAliases.domain == int(self.get_argument("domain"))).join(self.application.database.VirtualDomains),
                domains=self.application.database.VirtualDomains.select(),
                current_domain=self.get_argument("domain")
            )
        else:
            self.render(template,
                aliases=self.application.database.VirtualAliases.select().join(self.application.database.VirtualDomains),
                domains=self.application.database.VirtualDomains.select(),
                current_domain=0
            )

    @asynchronous
    @authenticated
    def post(self):
        template = self.template_path + "/aliases.template"
        if all(k in self.request.arguments for k in ("source", "destination", "domain")):
            self.application.database.VirtualAliases.create(
                source=self.get_argument('source'),
                destination=self.get_argument('destination'),
                domain=int(self.get_argument('domain'))
            )

        self.render(template,
            aliases=self.application.database.VirtualAliases.select().join(self.application.database.VirtualDomains),
            domains=self.application.database.VirtualDomains.select(),
            current_domain=0
        )