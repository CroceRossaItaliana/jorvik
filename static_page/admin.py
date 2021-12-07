from xlrd import open_workbook

from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import HttpResponse, redirect, render
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Page, TypeFormCompilati
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

    def _process_imported_file(self, file, imported_type):
        columns = {
            ImportAndGenerateStaticPage.CATALOGO_CORSI:
                ('Sigla Corso', 'Nome del Corso'),  #'Qualifica che si ottiene', 'Spiegazione del corso'),
            ImportAndGenerateStaticPage.GLOSSARIO_CORSI:
                ('Acronimo/termine', 'Significato')
        }

        table = ['<table width="100%">\n', '</table>']
        td = "<td>%s</td>\n\t" * len(columns[imported_type])
        tr = "<tr>\n\t%s</tr>\n" % td
        html = table[0] + tr % (columns[imported_type])

        xls = open_workbook(file_contents=file.read())
        sheet = xls.sheet_by_index(0)

        if imported_type == ImportAndGenerateStaticPage.GLOSSARIO_CORSI:
            for i in range(0, sheet.nrows):
                row = sheet.row_slice(i)
                sigla = row[0].value.strip()
                text = row[1].value.strip()
                html += tr % (sigla, text)

        elif imported_type == ImportAndGenerateStaticPage.CATALOGO_CORSI:
            for i in range(0, sheet.nrows):
                row = sheet.row_slice(i)

                if i == 0 or row[0].value == 'N.':
                    continue

                sigla = row[1].value.strip()
                text = row[2].value.strip()
                html += tr % (sigla, text)

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


@admin.register(TypeFormCompilati)
class TypeAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'comitato', 'persona', 'delega']
    raw_id_fields = ('comitato', 'persona',)
    search_fields = ['comitato__nome']
