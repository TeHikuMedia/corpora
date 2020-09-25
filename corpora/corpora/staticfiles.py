from django.contrib.staticfiles.apps import StaticFilesConfig

class CorporaStaticFilesConfig(StaticFilesConfig):
    ignore_patterns = ['CVS', '.*', '*~', 'node_modules/**', '*.md']
