from django.db.models import Sum, Q

from anagrafica.permessi.costanti import GESTIONE_SOCI
from .models import Quota, Tesseramento


class ReportRicevute:
    def __init__(self, me, form=None):
        self.me = me
        self.sedi = me.oggetti_permesso(GESTIONE_SOCI)

        # Initial values
        self.tipi = [x[0] for x in Quota.TIPO]
        self.anno = Tesseramento.ultimo_anno()

        if form is not None and form.is_valid():
            cd = form.cleaned_data
            self.tipi = cd.get('tipi_ricevute')
            self.anno = cd.get('anno')

    @property
    def tipi_testo(self):
        return [dict(Quota.TIPO)[t] for t in self.tipi]

    @property
    def queryset(self):
        return Quota.objects.filter(
            Q(Q(sede__in=self.sedi) | Q(appartenenza__sede__in=self.sedi)),
            anno=self.anno,
            tipo__in=self.tipi,
        ).order_by('progressivo')

    @property
    def importo_totale(self):
        non_annullate = self.queryset.filter(stato=Quota.REGISTRATA)
        importo = non_annullate.aggregate(Sum('importo'))['importo__sum'] or 0.0
        importo_extra = non_annullate.aggregate(Sum('importo_extra'))['importo_extra__sum'] or 0.0
        return importo + importo_extra

    def download(self):
        return
