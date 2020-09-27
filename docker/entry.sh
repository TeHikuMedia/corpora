#!/bin/bash
set -e

python /webapp/corpora/corpora/manage.py migrate --noinput
#python /webapp/corpora/corpora/manage.py bower_install --allow-root
python /webapp/corpora/corpora/manage.py collectstatic --noinput
python /webapp/corpora/corpora/manage.py loaddata /webapp/corpora/corpora/people/fixtures/iwi.yaml
python /webapp/corpora/corpora/manage.py shell -c "from django.db import DEFAULT_DB_ALIAS as database; from django.contrib import auth; model = auth.get_user_model(); model.objects.db_manager(database).create_superuser('docker','docker@email.com', 'password')" || true

exec "$@"
