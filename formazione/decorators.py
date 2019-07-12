from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser
from .models import Corso
from anagrafica.permessi.costanti import ERRORE_PERMESSI


def can_access_to_course(function):
    def wrapper(request, *args, **kwargs):
        me = request.me
        proceed = True
        REDIRECT_ERR = redirect(ERRORE_PERMESSI)

        if hasattr(me, 'dipendente') and me.dipendente:
            pass
        elif not hasattr(me, 'ha_aspirante'):
            proceed = False
        elif not me.ha_aspirante and not me.volontario:
            proceed = False

        if not proceed:
            return REDIRECT_ERR

        r = function(request, *args, **kwargs)
        try:
            context = r[1]  # response context stored in the view
        except IndexError:
            return r
        except AttributeError:
            if r and hasattr(r, 'status_code'):
                if r.status_code == 302:
                    return redirect(r.url)
        else:
            if not context:
                return r

        is_aspirante = me.ha_aspirante
        is_volontario = me.volontario

        # viste.aspirante_corso_base_informazioni
        if 'corso' in context:
            corso = context['corso']
            if corso.tipo == Corso.CORSO_NUOVO:
                # Aspirante can't access to CORSO_NUOVO page.
                if is_aspirante and not is_volontario:
                    return REDIRECT_ERR

        # viste.aspirante_corsi
        if 'corsi' in context:
            if is_aspirante and not is_volontario:
                # Update corsi queryset
                context['corsi'] = me.aspirante.corsi(tipo=Corso.BASE)
        return r

    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper
