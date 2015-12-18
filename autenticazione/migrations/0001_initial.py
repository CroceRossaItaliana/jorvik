# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Indirizzo email', unique=True)),
                ('ultimo_accesso', models.DateTimeField(null=True, blank=True, verbose_name='Ultimo accesso')),
                ('ultimo_consenso', models.DateTimeField(null=True, blank=True, verbose_name='Ultimo consenso')),
                ('is_staff', models.BooleanField(help_text="Se l'utente è un amministratore o meno.", verbose_name='Amministratore', default=False)),
                ('is_active', models.BooleanField(help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', verbose_name='Attivo', default=True)),
                ('groups', models.ManyToManyField(blank=True, related_query_name='user', related_name='user_set', to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('persona', models.OneToOneField(blank=True, to='anagrafica.Persona', null=True)),
                ('user_permissions', models.ManyToManyField(blank=True, related_query_name='user', related_name='user_set', to='auth.Permission', help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
