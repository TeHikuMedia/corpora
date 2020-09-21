from dal import autocomplete

from people.models import Tribe, Group


class TribeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Tribe.objects.all().order_by('name')

        # TO DO: use somethign like solr and index while ignoring diacritics
        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q).order_by('name')

        return qs


class GroupAutocomplete(autocomplete.Select2QuerySetView):
    create_field = 'name'

    def has_add_permission(self, request):
        # any authenticated user can add a group
        return request.user.is_authenticated

    def get_queryset(self):
        qs = Group.objects.all().order_by('name')

        if self.q:
            qs = qs.filter(name__unaccent__icontains=self.q).order_by('name')

        return qs
