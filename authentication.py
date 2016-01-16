__author__ = 'brayden'

import hashlib
import passlib.hash
import os
from peewee import DoesNotExist


class Authentication(object):
    class BadUser(Exception):
        def __init__(self, username):
            self.message = "Username %s does not exist" % username

    def __init__(self, application):  # the application object is the tornado.web.Application instance
        self.rounds = 1000
        self.application = application

    def check_credentials(self, username: str, password: str) -> bool:
        try:
            password_hash = self.application.database.Users.select(self.application.database.Users.Password).where(
                self.application.database.Users.Username == username).get().Password
        except DoesNotExist:
            raise self.BadUser(username)
        return passlib.hash.sha1_crypt.verify(password, password_hash)

    def _generate_session(self) -> str:
        return hashlib.sha512(os.urandom(128)).hexdigest()

    def _insert_session_db(self, username: str, session: str, ip: str):
        if len(session) > 128:
            raise Exception('Session is too long, should be 128 chars max, got ' + str(len(session)))

        self.application.database.Sessions.create(User=self.application.database.Users.select().where(
            self.application.database.Users.Username == username).get().ID, Session=session, IP=ip)

    def create_session(self, username: str, ip: str) -> str:
        session = self._generate_session()
        self._insert_session_db(username, session, ip)
        return session

    def get_sessions(self, username: str) -> str:
        try:
            return self.application.database.Sessions.select().where(
                self.application.database.Users.Username == username).get()
        except DoesNotExist:
            raise self.BadUser(username)

    def create_user(self, username: str, password: str):
        password = passlib.hash.sha1_crypt.encrypt(password, rounds=self.rounds)
        self.application.database.Users.create(Username=username, Password=password)

    def change_password(self, username: str, new_password: str):
        try:
            self.application.database.Users.update(
                Password=passlib.hash.sha1_crypt.encrypt(new_password, rounds=self.rounds)).where(
                self.application.database.Users.Username == username).execute()
        except DoesNotExist:
            raise self.BadUser(username)

    def check_session(self, username: str, session: str) -> bool:
        try:
            self.application.database.Sessions.select().where(self.application.database.Sessions.Session == session,
                                                              self.application.database.Sessions.User == self.application.database.Users.select().where(
                                                                  self.application.database.Users.Username == username).get().ID).get()
            return True
        except DoesNotExist:
            return False

    def get_user(self, username: str) -> object:
        try:
            return self.application.database.Users.get(self.application.database.Users.Username == username)
        except DoesNotExist:
            raise self.BadUser(username)

    def remove_session(self, session: str):
        try:
            self.application.database.Sessions.get(self.application.database.Sessions.Session == session).delete_instance()
        except DoesNotExist:
            pass