from __future__ import unicode_literals

from django.db import migrations, models


def update_select_modalita(apps, schema_editor):
    Titolo = apps.get_model('curriculum', 'Titolo')

    corsi = Titolo.objects.filter(tipo='TC', sigla__isnull=False)
    for corso in corsi:
        if corso.online:
            corso.modalita_titoli_cri = 'CO'
        else:
            corso.modalita_titoli_cri = 'CB'

        corso.save()


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0024_titolo_moodle'),
    ]

    operations = [
        migrations.AddField(
            model_name='titolo',
            name='modalita_titoli_cri',
            field=models.CharField(blank=True,
                                   choices=[('CB', 'Corso base'), ('CO', 'Corso online'),
                                            ('CE', 'Corso equipollenza')], db_index=True, max_length=2, null=True),
        ),
        migrations.RunPython(update_select_modalita),
        migrations.RemoveField(
            model_name='titolo',
            name='online',
        ),
    ]
