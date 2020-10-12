from rest_framework.throttling import UserRateThrottle

class CorporaUserRateThrottle(UserRateThrottle):
    '''
    Our special throttle that doesn't throttle staff
    or superusers. We should probably change this to
    be more specific around users and permissions.
    '''

    def allow_request(self, request, view):
        if (request.user.is_authenticated and 
                (request.user.is_staff or 
                 request.user.is_superuser)):
            return True
        else:
            return super().allow_request(request, view)
