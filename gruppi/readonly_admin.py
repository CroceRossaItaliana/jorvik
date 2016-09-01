from django.conf import settings

class ReadonlyAdminMixin(object):
    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name=settings.READONLY_GROUP).exists():
            return list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))
        else:
            return self.readonly_fields
