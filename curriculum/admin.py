from django.contrib import admin
from curriculum.models import TitoloPersonale, Competenza
from curriculum.models import Titolo
from curriculum.models import CompetenzaPersonale

admin.site.register(Competenza)
admin.site.register(CompetenzaPersonale)
admin.site.register(Titolo)
admin.site.register(TitoloPersonale)