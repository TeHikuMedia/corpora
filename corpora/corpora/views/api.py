from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from corpora.serializers import UserSerializer, GroupSerializer


class UserPermissions(permissions.BasePermission):
    """
    Only a user can edit his/her own info.
    """

    def has_permission(self, request, view):

        action = view.action

        if request.user.is_staff and request.user.is_authenticated:
            self.message = _("Only staff can view this information.")
            return True
        # elif view.action in 'update partial_update':
        #     return True
        else:
            self.message = _("You're not allowed to view this information.")
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff and request.user.is_authenticated:
            # Authenticated staff have full access
            return True
        else:

            if (request.user == obj):
                # Only a person can view/edit his/her own data
                if request.method in permissions.SAFE_METHODS:
                    # No authentication needed to view data
                    return True
                elif request.method in ['POST', 'PUT']:
                    return True  # No longer requiring authentication

                    # Authentication needed to edit data
                    self.message = _("You must sign in to edit your info.")
                    return request.user.is_authenticated
            else:
                self.message = _("You're not allowed to view this information.")
                return False
        self.message = _("You're not allowed to view this information.")
        return False


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermissions,)

    # def update(self, instance, validated_data):\

    #     return instance



class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
