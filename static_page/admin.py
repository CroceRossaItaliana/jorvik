from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import HttpResponse, redirect, render
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Page
from .forms import ImportAndGenerateStaticPage


@admin.register(Page)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug',]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(r'^import/$',
                self.admin_site.admin_view(self.import_and_generate_static_page),
                name='static_page_page_import_and_generate'),
        ]

        urls = custom_urls + urls
        return urls

    def _process_imported_file(self, file, type):
        import csv
        from io import StringIO

        columns = {
            ImportAndGenerateStaticPage.CATALOGO_CORSI:
                ('Sigla Corso', 'Nome del Corso',
                 'Qualifica che si ottiene', 'Spiegazione del corso'),
            ImportAndGenerateStaticPage.GLOSSARIO_CORSI:
                ('Acronimo/termine', 'Significato')
        }

        table = ['<table width="100%">\n', '</table>']
        td = "<td>%s</td>\n\t" * len(columns[type])
        tr = "<tr>\n\t%s</tr>\n" % td
        html = table[0] + tr % (columns[type])

        for line in csv.reader(StringIO(file.read().decode()), delimiter=';'):
            if type == ImportAndGenerateStaticPage.GLOSSARIO_CORSI:
                html += tr % tuple(i.strip() for i in line[0].split('-'))

            elif type == ImportAndGenerateStaticPage.CATALOGO_CORSI:
                # TODO: ...
                pass

        html += table[1]
        return html

    def import_and_generate_static_page(self, request):
        redirect_url = redirect(reverse("admin:static_page_page_changelist"))

        if request.method == 'POST':
            form = ImportAndGenerateStaticPage(request.POST, request.FILES)
            if form.is_valid():
                cd = form.cleaned_data
                imported_type, file = cd['type'], cd['file']
                file_processed = self._process_imported_file(file, imported_type)
                title = dict(ImportAndGenerateStaticPage.TYPE_CHOICES)[imported_type]

                page, created = Page.objects.get_or_create(slug=imported_type, title=title)
                if page:
                    page.text = file_processed
                    page.save()

                messages.success(request, 'I dati sono stati importati con successo!')
                return redirect_url
        else:
            form = ImportAndGenerateStaticPage()

        return render(request, 'import_and_generate_static_page.html', {
            'form': form
        })
