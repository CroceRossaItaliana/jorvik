from django.contrib.auth import get_permission_codename


class ReadonlyAdminMixin(object):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            view_permission = obj._meta.app_label + '.' + get_permission_codename('view', obj.__class__._meta)
            add_permission = obj._meta.app_label + '.' + get_permission_codename('add', obj.__class__._meta)
            if request.user.has_perm(view_permission) and not request.user.has_perm(add_permission):
                return list(set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))
            else:
                return self.readonly_fields
        else:
            return self.readonly_fields
