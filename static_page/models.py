from django.db import models

from anagrafica.models import Sede, Persona

from ckeditor.fields import RichTextField


class Page(models.Model):
    title = models.CharField(max_length=255)
    text = RichTextField('Corpo')
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Pagina statica'
        verbose_name_plural = 'Pagine statiche'


class TypeFormCompilati(models.Model):
    """
    Modello che registriamo i dati quando un Typeform e compilato
    """
    tipo = models.CharField(max_length=255, null=True, blank=True,
                            help_text="tipo di typeform (Transparenza, Autocontrollo, Fabbisogni, etc)")
    comitato = models.ForeignKey(Sede, on_delete=models.PROTECT)
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT)
    delega = models.CharField(max_length=255, null=True, blank=True,
                              help_text="questa puo esere utile quando l'utente non ha piu la delega che ha avuto "
                                        "quando ha compilato il typeform")

    def __str__(self):
        return str(self.tipo)

    class Meta:
        verbose_name = 'Typeform'
        verbose_name_plural = 'Typeformi'
