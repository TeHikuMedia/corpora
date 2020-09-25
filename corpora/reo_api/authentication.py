from rest_framework.authentication import TokenAuthentication
from .models import ApplicationAPI

class ApplicationAPITokenAuthentication(TokenAuthentication):
    model = ApplicationAPI
    keyword = 'AppToken'
