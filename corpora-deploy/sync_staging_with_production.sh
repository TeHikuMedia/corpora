### ONE WAY SYNC OF PRODUCTION BUCKET TO STAGING BUCKET ###

s3cmd sync s3://corpora-production-ap-southeast-2 s3://corpora-staging-ap-southeast-2 --dry-run --skip-existing --no-delete-removed
