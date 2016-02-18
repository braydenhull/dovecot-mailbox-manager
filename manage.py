from settings import Settings
from database import Database
from authentication import Authentication
import logging
import click
import getpass
import sys

# Credit to benbacardi for the colours library, which I stole this array from. https://github.com/benbacardi/colours
COLOURS = {
    'BLACK': '\033[30m',
    'BLUE': '\033[34m',
    'GREEN': '\033[32m',
    'CYAN': '\033[36m',
    'RED': '\033[31m',
    'PURPLE': '\033[35m',
    'YELLOW': '\033[33m',
    'LIGHT_GREY': '\033[37m',
    'DARK_GREY': '\033[1;30m',
    'BOLD_BLUE': '\033[1;34m',
    'BOLD_GREEN': '\033[1;32m',
    'BOLD_CYAN': '\033[1;36m',
    'BOLD_RED': '\033[1;31m',
    'BOLD_PURPLE': '\033[1;35m',
    'BOLD_YELLOW': '\033[1;33m',
    'BRIGHT_GREY': '\033[0;90m',
    'BRIGHT_BLUE': '\033[0;94m',
    'BRIGHT_GREEN': '\033[0;92m',
    'BRIGHT_CYAN': '\033[0;96m',
    'BRIGHT_RED': '\033[0;91m',
    'BRIGHT_PURPLE': '\033[0;95m',
    'BRIGHT_YELLOW': '\033[0;93m',
    'WHITE': '\033[1;37m',
    'NORMAL': '\033[0m',
}


class InstanceRepository:
    def __init__(self, debug=False):
        self.app_settings = Settings
        self.database = Database(self.app_settings.Database.DatabaseName, {'user': self.app_settings.Database.Username,
                                                                           'passwd': self.app_settings.Database.Password,
                                                                           'host': self.app_settings.Database.Address,
                                                                           'port': self.app_settings.Database.Port})
        self.authentication = Authentication(self)
        self.logger = logging.getLogger("manage.py")
        if debug:
            logging.basicConfig(level=logging.DEBUG)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(context, debug):
    context.obj = InstanceRepository(debug)

@cli.command("change_password")
@click.argument('username')
@click.pass_obj
def change_password(instance, username):
    try:
        instance.logger.debug("Getting database object for username, {username}".format(username=username))
        instance.authentication.get_user(username)
    except instance.authentication.BadUser:
        instance.logger.debug("Caught BadUser exception when grabbing user object")
        print("{colour}{username} doesn't exist! Exiting...{reset}".format(colour=COLOURS['RED'], username=username, reset=COLOURS['NORMAL']))
        sys.exit(1)

    print("{colour}This will reset the password for user {username}\r\nYou will be prompted for the password{reset}".format(colour=COLOURS['CYAN'], username=username, reset=COLOURS['NORMAL']))

    new_password = getpass.getpass("New Password: ")
    instance.logger.info("Updating password for {username}".format(username=username))
    instance.authentication.change_password(username, new_password)
    print("{colour}Successfully updated the password for {username}!{reset}".format(colour=COLOURS['GREEN'], username=username, reset=COLOURS['NORMAL']))

@cli.command("create_user")
@click.argument("username")
@click.pass_obj
def create_user(instance, username):
    try:
        instance.logger.debug("Checking if the username is already in use")
        instance.authentication.get_user(username)
        # uh oh.. user probably exists
        print("{colour}This username is already in use and usernames must be unique.{reset}".format(colour=COLOURS['RED'], reset=COLOURS['NORMAL']))
        sys.exit(1)
    except instance.authentication.BadUser:
        pass
    except Exception:
        print("{colour}An unexpected exception was thrown. Rethrowing...{reset}".format(colour=COLOURS['BRIGHT_RED'], reset=COLOURS['NORMAL']))
        raise

    print("{colour}This will create a new user for the web portal which will be immediately available.\r\n"
          "{reset}{bold}NOTE:{reset}{colour} Users are automatically administrators and there are no permissions!{reset}".format(colour=COLOURS['CYAN'], bold=COLOURS['BOLD_YELLOW'], reset=COLOURS['NORMAL']))

    instance.logger.debug("Grabbing password from user shell")
    password = getpass.getpass("Password: ")
    instance.logger.debug("Creating user")
    instance.authentication.create_user(username, password)
    instance.logger.debug("Created user")

    print("{colour}Successfully created {username}, if the web server is currently running, the user should be immediately available.{reset}".format(colour=COLOURS['GREEN'], username=username, reset=COLOURS['NORMAL']))

@cli.command("delete_user")
@click.argument("username")
@click.pass_obj
def delete_user(instance, username):
    try:
        instance.logger.debug("Grabbing user object instance")
        user = instance.authentication.get_user(username)
    except instance.authentication.BadUser:
        print("{colour}User '{username}' does not exist, exiting...{reset}".format(colour=COLOURS['RED'], username=username, reset=COLOURS['NORMAL']))
        sys.exit(1)

    print("{colour}This will delete user '{username}' immediately, there is no way to undo this. Are you sure?{reset}".format(colour=COLOURS['YELLOW'], username=username, reset=COLOURS['NORMAL']))
    answer = input("Confirm (Y/N): ")
    instance.logger.debug("Got answer: {answer}".format(answer=answer))

    if answer.lower().startswith('y'):
        user.delete_instance(recursive=True)
        print("{colour}Successfully deleted {username}.{reset}".format(colour=COLOURS['GREEN'], username=username, reset=COLOURS['NORMAL']))
    else:
        print("{colour}Exiting...{reset}".format(colour=COLOURS['RED'], reset=COLOURS['NORMAL']))

@cli.command("list_users")
@click.pass_obj
def list_users(instance):
    users = instance.database.Users.select()
    print("{colours}Users:{reset}".format(colours=COLOURS['GREEN'], reset=COLOURS['NORMAL']))
    for user in users:
        print("{colour}{username}{reset}".format(colour=COLOURS['CYAN'], username=user.Username, reset=COLOURS['NORMAL']))

    print("{colours}{number} users retrieved{reset}".format(colours=COLOURS['GREEN'], number=len(users), reset=COLOURS['NORMAL']))

if __name__ == '__main__':
    cli()