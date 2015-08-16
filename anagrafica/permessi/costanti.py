# coding=utf-8


"""
Questo file gestisce i permessi in Gaia.
 ============================================================================================
 |                                    ! HEEEEY, TU !                                        |
 ============================================================================================
  Prima di avventurarti da queste parti, assicurati di leggere la documentazione a:
   https://github.com/CroceRossaItaliana/jorvik/wiki/Deleghe,-Permessi-e-Livelli-di-Accesso
 ============================================================================================
"""

GESTIONE_SEDE = "GESTIONE_SEDE"
GESTIONE_SOCI = "GESTIONE_SOCI"
ELENCHI_SOCI = "ELENCHI_SOCI"
GESTIONE_ATTIVITA_SEDE = "GESTIONE_ATTIVITA_SEDE"
GESTIONE_ATTIVITA_AREA = "GESTIONE_ATTIVITA_AREA"
GESTIONE_ATTIVITA = "GESTIONE_ATTIVITA"
GESTIONE_CORSI_SEDE = "GESTIONE_CORSI_SEDE"
GESTIONE_CORSO = "GESTIONE_CORSO"

# Tipologia degli oggetti assegnati ad ogni Permesso.
PERMESSI_OGGETTI = (
    (GESTIONE_SEDE,             'Sede'),
    (GESTIONE_SOCI,             'Sede'),
    (ELENCHI_SOCI,              'Sede'),
    (GESTIONE_ATTIVITA_SEDE,    'Sede'),
    (GESTIONE_ATTIVITA_AREA,    'Area'),
    (GESTIONE_ATTIVITA,         'Attivita'),
    (GESTIONE_CORSI_SEDE,       'Sede'),
    (GESTIONE_CORSO,            'Corso'),
)


# Livelli di permesso
# IMPORTANTE: Tenere in ordine, sia numerico che di linea.

# - Scrittura e cancellazione
COMPLETO = 40

# - Scrittura
MODIFICA = 30

# - Scrittura dei dettagli
MODIFICA_TURNI = 25
MODIFICA_LEZIONI = MODIFICA_TURNI

# - Sola lettura
LETTURA = 10

# - Nessuno
NESSUNO = 0


# I permessi minimi per ogni tipo di oggetto.
#  Ad esempio, tutti i commenti sono pubblici. Ne segue,
#  che il permesso minimo per Commento sia LETTURA.
# Ove non specificato, il minimo e' NESSUNO.
# Utilizzare permesso_minimo(Tipo) per ottenere il minimo.
PERMESSI_MINIMO = {
 'Persona':   LETTURA,
 'Sede':      LETTURA,
 'Commento':  LETTURA,
}

def permesso_minimo(tipo):
    """
    Ritoran il permesso minimo globale per un detemrinato tipo.
    :param tipo: Un modello (ie. Persona, Sede, ecc.)
    :return: Il minimo, ie. NESSUNO o il minimo impostato.
    """
    tipo = tipo.__name__
    try:
        return PERMESSI_MINIMO[tipo]
    except KeyError:  # TOFIX
        return NESSUNO





# Tieni in memoria anche come dizionari, per lookup veloci
PERMESSI_OGGETTI_DICT = dict(PERMESSI_OGGETTI)

# Costanti URL
ERRORE_PERMESSI = '/errore/permessi/'
ERRORE_ORFANO = '/errore/orfano/'