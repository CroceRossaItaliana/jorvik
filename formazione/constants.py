from anagrafica.permessi import applicazioni


# Queste sono le principali tipologie di deleghe di persone che hanno
# accesso/potere sui corsi della formazione
FORMAZIONE_ROLES = [applicazioni.PRESIDENTE,  # Può creare
                    applicazioni.COMMISSARIO,  # Può creare
                    applicazioni.DIRETTORE_CORSO, # Accesso solo al corso delegato
                    applicazioni.RESPONSABILE_FORMAZIONE,  # Può creare
                    applicazioni.DELEGATO_OBIETTIVO_6, # Può crare
]
