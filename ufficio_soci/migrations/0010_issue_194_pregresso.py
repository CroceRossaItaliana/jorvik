# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date

from django.db import migrations, models
from django.db.models import Q


def forward_func(apps, schema_editor):
    Appartenenza = apps.get_model("anagrafica", "Appartenenza")

    inizio = fine = datetime.now()

    # Trova tutte le appartenenze doppie
    apps = Appartenenza.objects.filter(
        Q(inizio__lte=inizio),
        Q(Q(fine__isnull=True) | Q(fine__gt=fine)),
        confermata=True,
        membro='OR',
        persona_id__in=Appartenenza.objects.filter(
            Q(inizio__lte=inizio),
            Q(Q(fine__isnull=True) | Q(fine__gt=fine)),
            confermata=True,
            membro__in=('VO', 'SO', 'DI'),
        ).values_list('persona_id', flat=True)
    )

    problemi = 0
    for app in apps:  # Per ogni appartenenza ordinaria ancora attiva

        # Trova la nuova appartenenza (reclamata)
        app_nuova = Appartenenza.objects.filter(
            Q(inizio__lte=inizio),
            Q(Q(fine__isnull=True) | Q(fine__gt=fine)),
            confermata=True,
            persona=app.persona,
            membro__in=('VO', 'SO', 'DI'),
        ).order_by('-inizio').first()

        if app_nuova.inizio < app.inizio:  # Data sballata.
            app_nuova.inizio = datetime(2015, 1, 1)
            app_nuova.save()
            app.fine = app_nuova.inizio
            app.save()

        else:  # Solo da chiudere la vecchia.
            app.fine = app_nuova.inizio
            app.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0009_auto_20160224_1447'),
    ]

    operations = [
        migrations.RunPython(forward_func)
    ]
