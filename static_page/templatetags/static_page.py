from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def static_page_content_filter(context):
    from bs4 import BeautifulSoup

    page = context.get('page')

    # GAIA-271 (passaggio variabili comitato nel link report osservatorio)
    if page.pk == 4 or page.slug == 'report-violence':
        try:
            # Ottieni la sede di appartenenze volontario
            persona = context.request.user.persona
            app_vo = persona.appartenenza_volontario.last()
            if app_vo:
                sede = app_vo.sede

                # Modifica contenuto
                html = BeautifulSoup(page.text, 'lxml')
                link = html.find('a', id="aggressione-btn")
                href = link.get('href')
                link['href'] = "%s?nomec=%s&idc=%s" % (href, sede.nome, sede.pk)

                # get rid of html/body tags
                page.text = ''.join([str(x) for x in html.body.children])
        except:
            # se qualcosa vada storto - non casca niente.
            pass

    return page
