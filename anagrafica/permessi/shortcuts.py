from ..permessi.applicazioni import (PRESIDENTE, PERMESSI_NOMI, COMMISSARIO,
    PERMESSI_NOMI_DICT, UFFICIO_SOCI_UNITA, DELEGHE_RUBRICA, OBIETTIVI,
    DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_1,
    REFERENTE, DELEGATO_OBIETTIVO_4, RESPONSABILE_FORMAZIONE,
    DELEGATO_OBIETTIVO_6, DELEGATO_OBIETTIVO_5, RESPONSABILE_AUTOPARCO,
    DELEGATO_CO, DIRETTORE_CORSO, RESPONSABILE_AREA, CONSIGLIERE,
    CONSIGLIERE_GIOVANE, VICE_PRESIDENTE, CENTRO_FORMAZIONE_NAZIONALE)

from ..permessi.applicazioni import UFFICIO_SOCI, PERMESSI_NOMI_DICT

from ..permessi.costanti import (GESTIONE_ATTIVITA, PERMESSI_OGGETTI_DICT,
                                 GESTIONE_SOCI, GESTIONE_CORSI_SEDE, GESTIONE_CORSO, GESTIONE_SEDE,
                                 GESTIONE_AUTOPARCHI_SEDE, GESTIONE_CENTRALE_OPERATIVA_SEDE, GESTIONE_SO_SEDE)

from ..permessi.delega import delega_permessi, delega_incarichi

from ..permessi.incarichi import (INCARICO_GESTIONE_APPARTENENZE,
    INCARICO_GESTIONE_TRASFERIMENTI, INCARICO_GESTIONE_ESTENSIONI,
    INCARICO_GESTIONE_RISERVE, INCARICO_ASPIRANTE)

from ..permessi.persona import (persona_ha_permesso,
    persona_oggetti_permesso, persona_permessi, persona_permessi_almeno,
    persona_ha_permessi)
