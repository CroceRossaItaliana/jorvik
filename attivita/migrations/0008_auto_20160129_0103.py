# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attivita', '0007_auto_20160129_0053'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='attivita',
            index_together=set([('sede', 'estensione', 'apertura'), ('sede', 'estensione', 'apertura', 'stato'), ('sede', 'estensione'), ('sede', 'apertura'), ('estensione', 'apertura'), ('sede', 'estensione', 'stato')]),
        ),
    ]
