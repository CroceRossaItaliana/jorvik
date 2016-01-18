# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sangue', '0002_auto_20160117_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donatore',
            name='sede_sit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, null=True, to='sangue.Sede'),
        ),
        migrations.AlterField(
            model_name='donazione',
            name='sede',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='donazioni_sangue', null=True, to='sangue.Sede'),
        ),
    ]
