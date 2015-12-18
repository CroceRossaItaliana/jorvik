# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appartenenza',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, verbose_name='Confermata', db_index=True)),
                ('ritirata', models.BooleanField(default=False, verbose_name='Ritirata', db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Gruppo',
            fields=[
                ('conestensione_ptr', models.OneToOneField(serialize=False, to='base.ConEstensione', parent_link=True, primary_key=True, auto_created=True)),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=127)),
            ],
            options={
                'verbose_name_plural': 'Gruppi',
            },
            bases=('base.conestensione', models.Model),
        ),
    ]
