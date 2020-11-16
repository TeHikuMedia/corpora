from rest_framework.authentication import TokenAuthentication
from corpora.authentication import StagingTokenAuthentication
from reo_api.models import ApplicationAPI, UserAPI


class ApplicationAPITokenAuthentication(StagingTokenAuthentication, TokenAuthentication):
    model = ApplicationAPI
    keyword = 'AppToken'


class UserAPITokenAuthentication(StagingTokenAuthentication, TokenAuthentication):
    model = UserAPI
    keyword = 'UserToken'
