from django.db.backends.signals import connection_created


def pragma_synchronous_off(sender, connection, **kwargs):
    """Disable synchronous writes in sqlite."""
    if connection.vendor == "sqlite":
        cursor = connection.cursor()
        cursor.execute("PRAGMA synchronous=OFF;")


connection_created.connect(pragma_synchronous_off)
