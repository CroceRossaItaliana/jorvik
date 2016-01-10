# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Titolo',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('vecchio_id', models.IntegerField(default=None, blank=True, null=True, db_index=True)),
                ('tipo', models.CharField(max_length=2, choices=[('CP', 'Competenza Personale'), ('PP', 'Patente Civile'), ('PC', 'Patente CRI'), ('TS', 'Titolo di Studio'), ('TC', 'Titolo CRI')], db_index=True)),
                ('richiede_conferma', models.BooleanField(default=False)),
                ('richiede_data_ottenimento', models.BooleanField(default=False)),
                ('richiede_luogo_ottenimento', models.BooleanField(default=False)),
                ('richiede_data_scadenza', models.BooleanField(default=False)),
                ('richiede_codice', models.BooleanField(default=False)),
                ('inseribile_in_autonomia', models.BooleanField(default=True)),
                ('nome', models.CharField(max_length=255, db_index=True)),
            ],
            options={
                'verbose_name_plural': 'Titoli',
            },
        ),
        migrations.CreateModel(
            name='TitoloPersonale',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('confermata', models.BooleanField(default=True, db_index=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(default=False, db_index=True, verbose_name='Ritirata')),
                ('data_ottenimento', models.DateField(blank=True, help_text="Data di ottenimento del Titolo o Patente. Ove applicabile, data dell'esame.", null=True)),
                ('luogo_ottenimento', models.CharField(max_length=255, blank=True, help_text='Luogo di ottenimento del Titolo o Patente. Formato es.: Roma (RM).', null=True)),
                ('data_scadenza', models.DateField(blank=True, help_text='Data di scadenza del Titolo o Patente.', null=True)),
                ('codice', models.CharField(max_length=128, blank=True, help_text='Codice/Numero identificativo del Titolo o Patente. Presente sul certificato o sulla Patente.', null=True, db_index=True)),
                ('codice_corso', models.CharField(max_length=128, blank=True, null=True, db_index=True)),
                ('certificato', models.BooleanField(default=False)),
                ('certificato_da', models.ForeignKey(related_name='titoli_da_me_certificati', null=True, to='anagrafica.Persona')),
                ('persona', models.ForeignKey(to='anagrafica.Persona', related_name='titoli_personali')),
                ('titolo', models.ForeignKey(to='curriculum.Titolo')),
            ],
            options={
                'verbose_name_plural': 'Titoli personali',
                'verbose_name': 'Titolo personale',
            },
        ),
    ]
