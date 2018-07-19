
SCOPE_ANAGRAFICA_LETTURA_BASE = 'anagrafica_lettura_base'
SCOPE_ANAGRAFICA_LETTURA_COMPLETA = 'anagrafica_lettura_completa'
SCOPE_ANAGRAFICA_LETTURA_TELEFONO = 'anagrafica_lettura_telefono'
SCOPE_APPARTENENZE_LETTURA = 'appartenenze_lettura'


OAUTH2_PROVIDER = {
    'SCOPES': {
        SCOPE_ANAGRAFICA_LETTURA_BASE:     "Lettura anagrafica di base (nome, cognome, indirizzo email di contatto)",
        SCOPE_ANAGRAFICA_LETTURA_COMPLETA: "Lettura anagrafica completa (data e luogo di nascita, luogo di residenza, "
                                           "sesso e codice fiscale).",
        SCOPE_ANAGRAFICA_LETTURA_TELEFONO: "Lettura dei numeri di telefono",
        SCOPE_APPARTENENZE_LETTURA:        "Lettura delle appartenenze attuali",
    },

    'DEFAULT_SCOPES': [SCOPE_ANAGRAFICA_LETTURA_BASE]
}
