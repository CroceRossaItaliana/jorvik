from django.forms import modelformset_factory

from .forms import CorsoLinkForm, CorsoExtensionForm
from .models import CorsoFile, CorsoLink, CorsoEstensione


CorsoFileFormSet = modelformset_factory(CorsoFile,
    form=CorsoLinkForm, extra=1, max_num=5)

CorsoLinkFormSet = modelformset_factory(CorsoLink,
    fields=('link',), extra=1, max_num=5)

CorsoSelectExtensionFormSet = modelformset_factory(CorsoEstensione,
    extra=1, max_num=3, form=CorsoExtensionForm, can_delete=True)
