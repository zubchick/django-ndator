from django.core.management.base import inspectdbCommand

class Command(inspectdbCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        raise NotImplementedError()
