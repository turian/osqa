import os
from forum.models import KeyValue
from django.db import connection, transaction

KEY = 'PG_FTSTRIGGERS_VERSION'
VERSION = 3
install = False

try:
    version = KeyValue.objects.get(key=KEY).value
    if version < VERSION:
        install = True
except:
    install = True


if install:
    f = open(os.path.join(os.path.dirname(__file__), 'pg_fts_install.sql'), 'r')

    try:
        cursor = connection.cursor()
        cursor.execute(f.read())
        transaction.commit_unless_managed()

        try:
            kv = KeyValue.objects.get(key=KEY)
        except:
            kv = KeyValue(key=KEY)

        kv.value = VERSION
        kv.save()
        
    except Exception, e:
        #import sys, traceback
        #traceback.print_exc(file=sys.stdout)
        pass
    finally:
        cursor.close()

    f.close()
