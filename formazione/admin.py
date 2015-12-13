from django.contrib import admin
from formazione.models import CorsoBase, PartecipazioneCorsoBase, AssenzaCorsoBase, Aspirante

__author__ = 'alfioemanuele'


admin.site.register(CorsoBase)
admin.site.register(PartecipazioneCorsoBase)
admin.site.register(AssenzaCorsoBase)
admin.site.register(Aspirante)