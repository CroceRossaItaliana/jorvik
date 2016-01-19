# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    p = apps.get_model("anagrafica", "Persona")
    db_alias = schema_editor.connection.alias
    pp = p.objects.using(db_alias).filter(email_contatto__exact='').exclude(utenza__email__isnull=True)
    tot = pp.count()
    i = 0
    for x in pp:
        i += 1
        print("  Aggiornamento e-mail %d di %d" % (i, tot,))
        x.email_contatto = x.utenza.email
        x.save()

def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    a = 1  # do nothing


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0015_auto_20160119_1948'),

    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
