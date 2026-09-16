import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# If running in Vercel serverless without an external database, bootstrap SQLite in tempdir
if os.environ.get("VERCEL") and not os.environ.get("DATABASE_URL"):
    try:
        from django.core.management import call_command
        from django.db import connection

        if "public_site_schoolprofile" not in connection.introspection.table_names():
            call_command("migrate", interactive=False, verbosity=0)
            call_command("seed_data", verbosity=0)
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception("Vercel database bootstrap failed: %s", e)
