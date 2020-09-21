#!/bin/bash
input="/webapp/local.env"
while IFS= read -r line
do
	export $line
done < "$input"

python /webapp/corpora/corpora/manage.py compilemessages
python /webapp/corpora/corpora/manage.py bower_install --allow-root
python /webapp/corpora/corpora/manage.py collectstatic --clear --noinput
