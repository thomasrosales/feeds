import base64

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "The encoding script to get your username and password base64 to use as Basic Authentication"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        username_password = bytes(f"{username}:{password}", "utf-8")
        # https://docs.python.org/es/3/library/base64.html
        basic_authentication_decoded = base64.b64encode(username_password)
        self.stdout.write(self.style.SUCCESS(f'Successfully created "{basic_authentication_decoded.decode("utf-8")}"'))
