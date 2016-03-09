# -*- coding: utf-8 -*-

import os, sys
import random



os.environ['DJANGO_SETTINGS_MODULE'] = 'jorvik.settings'


from django.db import transaction

from veicoli.models import Collocazione, Veicolo

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

with transaction.atomic():
    ids = Collocazione.query_attuale().values_list("veicolo")
    veicoli = Veicolo.objects.all().exclude(id__in=ids)

    print("veicoli senza collocazione attuale")
    print(len(veicoli))

    for veicolo in veicoli:
        c = Collocazione.objects.filter(veicolo=veicolo).order_by("-fine").first()
        if not c:
            print("yolo")
            continue
        c.fine = None
        c.save()

