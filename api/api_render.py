from django.http import (
    HttpResponse, JsonResponse, )
from django.shortcuts import render
from django.template.context import _current_app_undefined
from django.template.engine import (
    _context_instance_undefined, _dictionary_undefined, _dirs_undefined,
)
from json_views.views import JSONDataView


class JSONGenericPage(JSONDataView):

    status_code = 200

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return

    def has_header(self, v):
        return False

    def get_context_data(self, **kwargs):
        context = super(JSONGenericPage, self).get_context_data(**kwargs)
        context = context
        return context


def api_render(request, template_name, context=None,
               context_instance=_context_instance_undefined,
               content_type=None, status=None, current_app=_current_app_undefined,
               dirs=_dirs_undefined, dictionary=_dictionary_undefined,
               using=None):
    print('son qui')
    if request.META.get('HTTP_DAMMELIJSON') == 'true':
        payload = JSONGenericPage(context=context)
        return JsonResponse(JSONGenericPage().render_to_response(context), safe=False)
    else:
        return render(request, template_name, context=None,
                      context_instance=context_instance,
                      content_type=content_type, status=status, current_app=current_app,
                      dirs=dirs, dictionary=dictionary,
                      using=using)
