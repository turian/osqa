import os

from django.db import connection, transaction
from django.conf import settings

import forum.models

def install_pg_fts(**kwargs):
    f = open(os.path.join(os.path.dirname(__file__), 'pg_fts_install.sql'), 'r')

    try:
        cursor = connection.cursor()
        cursor.execute(f.read())
        transaction.commit_unless_managed()
    except:
        pass
    finally:
        cursor.close()

    f.close()

if settings.DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql', ):
    from django.db.models.signals import post_syncdb
    post_syncdb.connect(install_pg_fts, sender=forum.models, weak=False)


try:
    from south.signals import post_migrate
    post_migrate.connect(install_pg_fts, weak=False)
except:
    pass