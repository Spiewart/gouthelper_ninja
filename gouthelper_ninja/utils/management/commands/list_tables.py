from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List all database tables"

    def handle(self, *args, **options):
        tables = [
            m._meta.db_table  # noqa: SLF001
            for c in apps.get_app_configs()
            for m in c.get_models()
        ]
        self.stdout.write(str(tables))
