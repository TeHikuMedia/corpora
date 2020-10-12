from rest_framework.authentication import TokenAuthentication
from reo_api.models import ApplicationAPI, UserAPI


class ApplicationAPITokenAuthentication(TokenAuthentication):
    model = ApplicationAPI
    keyword = 'AppToken'


class UserAPITokenAuthentication(TokenAuthentication):
    model = UserAPI
    keyword = 'UserToken'
