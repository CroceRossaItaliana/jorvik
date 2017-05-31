# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from base.utils import normalizza_nome, TitleCharField


def forwards_func(apps, schema_editor):
    Persona = apps.get_model('anagrafica', "Persona")
    db_alias = schema_editor.connection.alias
    for persona in Persona.objects.using(db_alias).all():
        nome = normalizza_nome(persona.nome)
        cognome = normalizza_nome(persona.cognome)
        if (persona.nome != nome) or (persona.cognome != cognome):
            persona.nome = nome
            persona.cognome = cognome
            persona.save()


class Migration(migrations.Migration):
    dependencies = [
        ('anagrafica', '0047_auto_20170525_2011'),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]
