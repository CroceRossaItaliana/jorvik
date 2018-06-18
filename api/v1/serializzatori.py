from anagrafica.models import Persona, Sede
from base.geo import Locazione
from base.tratti import ConStorico


def _campo(id, descrizione):
    return {"id": id,
            "descrizione": descrizione}


def luogo(comune, stato, provincia=None, cap=None,
          indirizzo=None, via=None, civico=None,
          regione=None):
    dati = {"comune": comune,
            "stato": str(stato)}

    if provincia:
        dati.update({"provincia": provincia})

    if cap:
        dati.update({"cap": cap})

    if indirizzo:
        dati.update({"indirizzo": indirizzo})

    if via:
        dati.update({"via": via})

    if civico:
        dati.update({"civico": civico})

    if regione:
        dati.update({"regione": regione})

    return dati


def luogo_di_nascita(persona):
    return luogo(comune=persona.comune_nascita,
                 provincia=persona.provincia_nascita,
                 stato=persona.stato_nascita)


def luogo_di_residenza(persona):
    return luogo(indirizzo=persona.indirizzo_residenza,
                 comune=persona.comune_residenza,
                 provincia=persona.provincia_residenza,
                 stato=persona.stato_residenza,
                 cap=persona.cap_residenza)


def locazione(locazione):
    assert isinstance(locazione, Locazione)
    return luogo(comune=locazione.comune,
                 stato=locazione.stato,
                 via=locazione.via,
                 civico=locazione.civico,
                 provincia=locazione.provincia,
                 regione=locazione.regione,
                 cap=locazione.cap)


def persona_anagrafica_base(persona):
    assert isinstance(persona, Persona)
    dati = {"id": persona.pk,
            "nome_completo": persona.nome_completo,
            "nome": persona.nome,
            "cognome": persona.cognome}
    if persona.email is not None:
        dati.update({"email": persona.email})
    return dati


def persona_anagrafica_completa(persona):
    assert isinstance(persona, Persona)
    dati = persona_anagrafica_base(persona)
    dati.update({"luogo_di_nascita": luogo_di_nascita(persona),
                 "luogo_di_residenza": luogo_di_residenza(persona),
                 "sesso": persona.genere,
                 "codice_fiscale": persona.codice_fiscale})
    return dati


def _con_storico(oggetto_con_storico):
    assert isinstance(oggetto_con_storico, ConStorico)
    return {"inizio": oggetto_con_storico.inizio,
            "fine": oggetto_con_storico.fine}


def sede(_sede, includi_comitato=True):
    assert isinstance(_sede, Sede)
    dati = {"nome": _sede.nome,
            "estensione": _campo(_sede.estensione, _sede.get_estensione_display()),
            "tipo": _campo(_sede.tipo, _sede.get_tipo_display())}

    if _sede.locazione:
        dati.update({"locazione": locazione(_sede.locazione)})

    if _sede.comitato and includi_comitato:
        dati.update({"comitato": sede(_sede.comitato, includi_comitato=False)})

    return dati


def appartenenza(appartenenza):
    dati = {}
    dati.update(_con_storico(appartenenza))
    dati.update({"tipo": _campo(id=appartenenza.membro, descrizione=appartenenza.get_membro_display()),
                 "sede": sede(appartenenza.sede)})
    return dati



