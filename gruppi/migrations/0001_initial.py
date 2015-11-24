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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(verbose_name='Confermata', db_index=True, default=True)),
                ('ritirata', models.BooleanField(verbose_name='Ritirata', db_index=True, default=False)),
            ],
            options={
                'verbose_name_plural': 'Appartenenze',
            },
        ),
        migrations.CreateModel(
            name='Gruppo',
            fields=[
                ('conestensione_ptr', models.OneToOneField(primary_key=True, to='base.ConEstensione', serialize=False, auto_created=True, parent_link=True)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('nome', models.CharField(verbose_name='Nome', max_length=127)),
            ],
            options={
                'verbose_name_plural': 'Gruppi',
            },
            bases=('base.conestensione', models.Model),
        ),
    ]
