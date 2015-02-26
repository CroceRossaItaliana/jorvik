## Come gestire i permessi in Gaia

### Controllare i permessi

```python
def attivita_turni_modifica(request, attivita_id):

    attivita = Attivita.objects.get(pk=attivita_id) 
    persona = request.user.persona # Il mio utente
    
    if not permessi_minimi_persona(persona, attivita, MODIFICA_TURNI)
        return PERMESSO_NEGATO # :(

    print("Yaay! %s può modificare turni %s" % (persona, attivita))

    # ...
```
 
### Aggiungere una nuova delega

1. In `permessi.costanti`:
  * Crea una nuova costante in testa al file col nome della tua nuova delega;
  * Modifica `PERMESSI_NOMI` aggiungendo il nome esteso della tua applicazione;
  * Modifica `PERMESSI_OGGETTI` aggiungendo il tipo di oggetto sul quale agisce;
  
2. In `permessi.funzioni`:
  * Crea una funzione `permessi_tua_app`, che prenda come primo argomento un oggetto del tipo da te specificato
    e, come secondo argomento, un oggetto generico. La tua funzione deve testare il tipo di questo oggetto e
    -qualora questo sia di interesse per la tua applicazione- esaminarlo e ritornare il livello di permesso
    appropriato, sotto forma di una costante di livello di permesso in `permessi.costanti`.
    Se nessun permesso e' appropriato, ritorna `None`.
    
3. In `permessi.costanti`:
  * Modifica `PERMESSI_FUNZIONI` aggiungendo una riga con la tua delega e la funzione permessi appena creata.

4. (!TODO: Aggiungere al pannello appropriato per la gestione delle deleghe)

5. Fine!
