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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(unique=True, verbose_name='Indirizzo email', max_length=254)),
                ('ultimo_accesso', models.DateTimeField(blank=True, null=True, verbose_name='Ultimo accesso')),
                ('ultimo_consenso', models.DateTimeField(blank=True, null=True, verbose_name='Ultimo consenso')),
                ('is_staff', models.BooleanField(help_text="Se l'utente è un amministratore o meno.", default=False, verbose_name='Amministratore')),
                ('is_active', models.BooleanField(help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', default=True, verbose_name='Attivo')),
                ('groups', models.ManyToManyField(to='auth.Group', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', verbose_name='groups', blank=True)),
                ('persona', models.OneToOneField(to='anagrafica.Persona', null=True, blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', related_name='user_set', help_text='Specific permissions for this user.', related_query_name='user', verbose_name='user permissions', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
