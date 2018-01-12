# Gaia Jovik

Jorvik è il nome in codice del progetto di ridisegno del software del **Progetto Gaia** Croce Rossa Italiana
([GitHub](https://github.com/CroceRossaCatania/gaia), [Web](https://gaia.cri.it)).


I punti chiave nella riprogettazione sono i seguenti:
* Raccogliere il feedback ottenuto tramite <feedback@gaia.cri.it>,
* Raccogliere le necessità espresse dagli utenti tramite il Supporto,
* Raccogliere le nuove necessità dell'Associazione,

## Segnalazioni tecniche / Issues

Le segnalazioni sono state spostate da GitHub al [**nuovo sistema di tracciamento issues**](https://jira.gaia.cri.it/issues) utilizzato dal Progetto Gaia (JIRA). Vedi l'articolo "[Segnalazioni tecniche](https://github.com/CroceRossaItaliana/jorvik/wiki/Segnalazioni-tecniche)" sul wiki per maggiori informazioni sul come utilizzarlo.


## Sviluppo

Sei interessato a partecipare allo sviluppo di Gaia/Jorvik? Contattaci all'indirizzo e-mail <sviluppo@gaia.cri.it>!

### Integrazione continua

Jorvik viene installato e testato sulle recenti versioni di Python 3, in modo automatico, da Travis CI ad ogni push.

* Stato attuale di `master` (sviluppo): [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=master)](https://travis-ci.org/CroceRossaItaliana/jorvik)
* Stato attuale di `produzione` (online*): [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=produzione)](https://travis-ci.org/CroceRossaItaliana/jorvik)

\*: *Il deployment non viene ancora effettuato automaticamente.*


### Ambienti di staging e test

Gli ambienti di staging e test sono orchestrati automaticamente da [Wonderbot](https://github.com/CroceRossaItaliana/wonderbot), e sono accessibili al seguente indirizzo:

**[http://wonderbot.gaia.cri.it/](http://wonderbot.gaia.cri.it/)**

Alcune note:

* Gli ambienti di sviluppo e staging sono ospitati presso la macchina dedicata per la squadra di supporto e sviluppo,
* Le installazioni su questa macchina si aggiornano automaticamente col codice del relativo branch di staging,
* Il database viene scaricato settimanalmente dalla installazione in produzione, e tutte le modifiche effettuate nella settimana precedente vengono distrutte,
* Le installazioni di staging **non** sono in grado di inoltrare i messaggi di posta -nonostante si illudano di farlo correttamente-,
* Inoltre, le procedure programmate e periodiche (cron jobs) non vengono eseguite su queste installazioni,
* Le installazioni sono da considerarsi condivise e, nel caso di utilizzo, l'utente non deve aspettarsi alcuna forma di privacy relativamente ai dati inseriti, garanzia sul servizio, o alcuna forma di affetto da parte degli sviluppatori,
* L'accesso agli ambienti di sviluppo/test è riservato al personale tecnico.


### Documentazione

Puoi trovare la **[Documentazione sul Wiki del progetto](https://github.com/CroceRossaItaliana/jorvik/wiki)**.

### Requisiti

* **[Python 3.4 e superiore](https://www.python.org/downloads/)** (es. `python3`)
* **[PIP 3](https://www.python.org/downloads/)** (es. `pip3`)
* **[PostgreSQL](http://www.postgresql.org/) 9.4+** con [PostGIS](http://postgis.net/))
* **[GEOS](http://trac.osgeo.org/geos/)** (Geometry Engine Open Source)
* **Linux**, Mac OS X e, probabilmente, Windows Server 2008 o 7 e superiori

### Ambiente di sviluppo

Per la configurazione automatica dell'ambiente di sviluppo su **Linux, Mac OS X 10.9+ e Windows 10**, è possibile usare Docker CE con Docker Compose. Docker Compose gestisce la creazione e la configurazione automatica (orchestration) di una insieme di container Docker.


1. **Scarica Docker CE** (o EE) da [docker.com](https://www.docker.com/community-edition),
2. **Scarica Docker Compose** da [docker.com](https://docs.docker.com/compose/install/),
3. **Scarica Jorvik** usando Git ([GitHub Desktop](https://desktop.github.com/) per Windows e Mac OS X, o da terminale come segue)

    ```bash
    $ git clone --recursive https://github.com/CroceRossaItaliana/jorvik
    ```
4. **Aprire un terminale** (prompt dei Comandi su Windows) e accedere alla cartella dove risiede il codice appena scaricato.

   ```bash
   $ cd jorvik
   ```
5. **Avvia Gaia** con Docker Compose (la prima volta potrebbe volerci un po')

    ```bash
    $ docker-compose up
    ```

   Questo avviera' i container necessari per lo sviluppo ed il testing di Gaia (web, database, pdf, selenium).

6. **Installare PyCharm Professional** da [JetBrains](https://www.jetbrains.com/pycharm/). La licenza e' gratis per gli studenti. Contattaci se necessiti di una licenza per lavorare su Jorvik: abbiamo un numero limitato di licenze per i volontari, quindi approfitta del trial di 30 giorni per assicurarti di voler collaborare.
6. **Configurare PyCharm per usare l'interprete del container Docker**:
  * Preferenze > Progetto > Interprete > Aggiungi interprete remoto
    ![image](https://cloud.githubusercontent.com/assets/621062/10762277/4da18088-7cbd-11e5-924e-a2737d7783e1.png)

  * Scegliere **"Docker-Compose"** e **`web`** come da immagine, e cliccare OK
    ![image](https://user-images.githubusercontent.com/621062/34888028-7a95f13e-f7c0-11e7-9eaa-e6bad16c7f51.png)

  * Assicurarsi che l'interprete "Remote Python 3.x Docker..." sia ora selezionato come predefinito per il progetto, quindi cliccare OK

6. **Usare il tasto "Run" su PyCharm** per controllare e avviare il server
  ![image](https://cloud.githubusercontent.com/assets/621062/10762357/abcb3050-7cbd-11e5-9fdf-c08a0b439369.png)


#### Docker Compose

* **Configurare (primo avvio) e avviare i container di Gaia**

    ```bash
    $ docker-compose up
    ```

* **Arrestare Gaia**

    ```bash
    $ docker-compose stop
    ```

* **Cancellare e riconfigurare i container da zero**

    ```bash
    $ docker-compose stop && docker-compose rm && docker-compose up --build
    ```

* **Eseguire comandi sulla macchina Web (Django)**

    ```bash
    # Shell di Django
    $ docker-compose exec web python manage.py shell

    # Bash
    $ docker-compose exec web bash
    ```


### Autenticazione a due fattori

Attualmente la piattaforma supporta la 2FA con:

 * Google Authenticator (e sistemi simili di OTP via QR Code)
 * Yubikey
 
Per il setup di Yubikey si veda: http://django-two-factor-auth.readthedocs.io/en/stable/installation.html#yubikey-setup

Per attivare la 2FA per un utente è sufficiente:

 * Installare Google Authenticator sul proprio dispositivo mobile
 * Fare il login normalmente nel pannello admin (`/admin`)
 * Selezionare la voce "Two factor auth" nel menù admin
 * Seguire le istruzioni dello wizard
 * Selezionare "Token generator" fra le opzioni
 * Scansionare con Google Authenticator il codice QR mostrato
 * Inserire il token generato da Google Authenticator
 * Il dispositivo è adesso autenticato
 
