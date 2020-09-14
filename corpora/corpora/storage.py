from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import get_storage_class

# Do We still need this? - https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
# https://stackoverflow.com/questions/18536576/how-can-i-use-django-storages-for-both-media-and-static-files
class S3StaticStorage(S3Boto3Storage):

    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = settings.AWS_STATIC_BUCKET_NAME
        kwargs['default_acl'] = settings.AWS_STATIC_DEFAULT_ACL
        # kwargs['acl'] = settings.AWS_STATIC_DEFAULT_ACL
        # kwargs['bucket'] = settings.AWS_STATIC_BUCKET_NAME
        super(S3StaticStorage, self).__init__(*args, **kwargs)


class CachedS3BotoStorage(S3StaticStorage):
    """
    S3 storage backend that saves the files locally, too.
    """
    def __init__(self, *args, **kwargs):
        super(CachedS3BotoStorage, self).__init__(*args, **kwargs)
        self.local_storage = get_storage_class(
            "compressor.storage.CompressorFileStorage")()

    def save(self, name, content):
        self.local_storage._save(name, content)
        super(CachedS3BotoStorage, self).save(name, self.local_storage._open(name))
        return name
