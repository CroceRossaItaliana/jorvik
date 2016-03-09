from django.utils import timezone
from django.db import migrations
from django.db.models import Q


def fix_collocazioni(apps, schema_editor):

    Collocazione = apps.get_model("veicoli", "Collocazione")
    Veicolo = apps.get_model("veicoli", "Veicolo")

    inizio = fine = timezone.now()

    ids = Collocazione.objects.filter(Q(inizio__lte=inizio),Q(Q(fine__isnull=True) | Q(fine__gt=fine))).values_list("veicolo")
    veicoli = Veicolo.objects.all().exclude(id__in=ids)

    print("veicoli senza collocazione attuale")
    print(len(veicoli))

    for veicolo in veicoli:
        c = Collocazione.objects.filter(veicolo=veicolo).order_by("-fine").first()
        if not c:
            print("yolo")
            continue
        c.fine = None
        c.save()



class Migration(migrations.Migration):

    dependencies = [
        ('veicoli', '0007_auto_20160225_2029'),

    ]

    operations = [
        migrations.RunPython(fix_collocazioni),
    ]