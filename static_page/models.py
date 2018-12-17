from django.db import models

from ckeditor.fields import RichTextField


class Page(models.Model):
    title = models.CharField(max_length=255)
    text = RichTextField('Corpo')
    slug = models.SlugField(max_length=255)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Pagina static'
        verbose_name_plural = 'Pagine statiche'
