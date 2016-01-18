# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    aut = apps.get_model("base", "Autorizzazione")
    db_alias = schema_editor.connection.alias
    aut.objects.using(db_alias).filter(concessa=True).update(necessaria=False)
    aut.objects.using(db_alias).filter(concessa=False).update(necessaria=False)


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    a = 1  # do nothing


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0011_auto_20160117_2143'),

    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
