# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from base.utils import normalizza_nome, TitleCharField


def forwards_func(apps, schema_editor):
    p = apps.get_model("anagrafica", "Persona")
    for x in p.objects.all():
        x.nome = normalizza_nome(x.nome)
        x.cognome = normalizza_nome(x.cognome)
        x.save()


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0039_issue201_ragione_sociale_comitati'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='cognome',
            field=TitleCharField(db_index=True, max_length=64, verbose_name='Cognome'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='nome',
            field=TitleCharField(db_index=True, max_length=64, verbose_name='Nome'),
        ),
        migrations.RunPython(forwards_func),
    ]
