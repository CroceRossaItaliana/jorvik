def access_to_courses(function):
    from django.shortcuts import redirect
    from .models import Corso
    from anagrafica.permessi.costanti import ERRORE_PERMESSI

    def wrapper(request, *args, **kwargs):
        me = request.me

        if not me.ha_aspirante:
            return redirect(ERRORE_PERMESSI)

        r = function(request, *args, **kwargs)
        try:
            context = r[1]  # response context stored in the view
        except IndexError:
            return r
        else:
            context = r[1] if len(r) >= 2 else None
            if context and ('corsi' in context):
                is_aspirante = me.ha_aspirante
                is_volontario = me.volontario

                # Filter displayed courses by membership of Persona (nel raggio)
                params = dict()
                if is_aspirante:
                    params = {'tipo': Corso.BASE}
                if is_volontario:
                    params = {'tipo': Corso.CORSO_NUOVO}

                # Update context data with new queryset
                context['corsi'] = me.aspirante.corsi(**params)
        return r

    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper