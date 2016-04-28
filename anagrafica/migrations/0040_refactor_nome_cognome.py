# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from base.utils import normalizza_nome, TitleCharField


def forwards_func(apps, schema_editor):
    p = apps.get_model('anagrafica', "Persona")
    db_alias = schema_editor.connection.alias
    for x in p.objects.using(db_alias).all():
        nomeNorm = normalizza_nome(x.nome)
        cognomeNorm = normalizza_nome(x.cognome)
        if (x.nome!=nomeNorm) or (x.cognome!=cognomeNorm) :
            x.nome = normalizza_nome(x.nome)
            x.cognome = normalizza_nome(x.cognome)
            x.save()


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0039_issue201_ragione_sociale_comitati'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
