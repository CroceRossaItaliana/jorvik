# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Indirizzo email')),
                ('ultimo_accesso', models.DateTimeField(blank=True, verbose_name='Ultimo accesso', null=True)),
                ('ultimo_consenso', models.DateTimeField(blank=True, verbose_name='Ultimo consenso', null=True)),
                ('is_staff', models.BooleanField(help_text="Se l'utente è un amministratore o meno.", default=False, verbose_name='Amministratore')),
                ('is_active', models.BooleanField(help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', default=True, verbose_name='Attivo')),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', related_query_name='user', related_name='user_set', blank=True, to='auth.Group')),
                ('persona', models.OneToOneField(blank=True, to='anagrafica.Persona', null=True)),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', verbose_name='user permissions', related_query_name='user', related_name='user_set', blank=True, to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
