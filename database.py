__author__ = 'brayden'

from peewee import *
from datetime import datetime


class Database:
    def __init__(self, database: str, settings: dict):
        self.database = MySQLDatabase(database, **settings)
        self.database.connect()

        class VirtualDomains(Model):
            id = PrimaryKeyField()
            name = CharField(max_length=50, null=False, unique=True)

            class Meta:
                database = self.database
                db_table = "virtual_domains"


        class VirtualUsers(Model):
            id = PrimaryKeyField()
            domain = ForeignKeyField(VirtualDomains, related_name="VirtualUsersDomain")
            password = CharField(max_length=200, null=False)
            email = CharField(max_length=250, null=False)

            class Meta:
                database = self.database
                db_table = "virtual_users"


        class VirtualAliases(Model):
            id = PrimaryKeyField()
            domain = ForeignKeyField(VirtualDomains, related_name="VirtualAlisesDomain")
            source = CharField(max_length=250, null=False)
            destination = CharField(max_length=250, null=False)

            class Meta:
                database = self.database
                db_table = "virtual_aliases"


        class Users(Model):
            ID = PrimaryKeyField()
            Username = CharField(max_length=128, unique=True)
            Password = CharField(max_length=100)
            DateJoined = DateTimeField(default=datetime.now)

            class Meta:
                database = self.database
                db_table = "WebUsers"


        class Sessions(Model):
            ID = PrimaryKeyField()
            User = ForeignKeyField(Users)
            Session = CharField(max_length=128)
            StartTime = DateTimeField(default=datetime.now)
            IP = CharField(max_length=64)

            class Meta:
                database = self.database
                db_table = "WebSessions"


        self.VirtualDomains = VirtualDomains
        self.VirtualUsers = VirtualUsers
        self.VirtualAliases = VirtualAliases
        self.Users = Users
        self.Sessions = Sessions

    def initialise(self):
        self.VirtualDomains.create_table(True)
        self.VirtualUsers.create_table(True)
        self.VirtualAliases.create_table(True)
        self.Users.create_table(True)
        self.Sessions.create_table(True)

    def is_populated(self) -> bool:
        try:
            self.Users.get(self.Users.ID == 1)
            return True
        except Exception:
            return False

    def ping(self):
        self.database.execute_sql('/* PING */ SELECT 1') # Connection needs to be pinged to keep it open