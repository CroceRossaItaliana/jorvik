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

#### Sviluppo

Per lo sviluppo di Jorvik, potrai utilizzare i container già pronti che ti permetteranno
di lavorare su Gaia senza la necessità di configurare manualmente un sistema di produzione.

* **[Docker CE](https://www.docker.com/community-edition)** (o EE)
* **[Python 3.4 e superiore](https://www.python.org/downloads/)**
* **[Docker Compose](https://docs.docker.com/compose/install)**
* **Linux, OS X o Windows 10**, ovvero qualunque OS che supporta i requisiti sopra elencati.


#### Produzione

Se vuoi configurare manualmente un sistema di produzione, puoi installare manualmente
i requisiti necessari. A meno che tu abbia intenzione di mettere online un *fork* di Gaia
su di un ambiente di produzione, questo è un metodo sconsigliato.

* **[Python 3.4 e superiore](https://www.python.org/downloads/)** (es. `python3`)
* **[PIP 3](https://www.python.org/downloads/)** (es. `pip3`)
  * Usa quindi PIP per installare tutti i requisiti Python, che sono specificati [requirements.txt](requirements.txt).
* **[PostgreSQL](http://www.postgresql.org/) 9.4+** con [PostGIS](http://postgis.net/))
* **[GEOS](http://trac.osgeo.org/geos/)** (Geometry Engine Open Source)
* **[Redis](https://redis.io/)**, o un altro broker supportato da [Celery](http://www.celeryproject.org/).
* **Linux**.

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
5. **Installare PyCharm Professional** da [JetBrains](https://www.jetbrains.com/pycharm/). La licenza e' gratis per gli studenti. Contattaci se necessiti di una licenza per lavorare su Jorvik: abbiamo un numero limitato di licenze per i volontari, quindi approfitta del trial di 30 giorni per assicurarti di voler collaborare.
6. **Configurare PyCharm per usare l'interprete del container Docker**:
    * Preferenze > Progetto > Interprete > Aggiungi interprete remoto ([Vedi immagine](https://cloud.githubusercontent.com/assets/621062/10762277/4da18088-7cbd-11e5-924e-a2737d7783e1.png))
    * Scegliere **"Docker-Compose"** e **`web`** come da immagine, e cliccare OK. ([Vedi immagine](https://user-images.githubusercontent.com/621062/34888028-7a95f13e-f7c0-11e7-9eaa-e6bad16c7f51.png))
    * Assicurarsi che l'interprete "Remote Python 3.x Docker..." sia ora selezionato come predefinito per il progetto, quindi cliccare OK
7. **Installa i dati di esempio**, scegliendo la configurazione `[jorvik] installa dati di esempio`** su PyCharm e premendo il taso "Run" ([Vedi immagine](https://user-images.githubusercontent.com/621062/39449785-eaa78f0a-4cc0-11e8-8e0d-a6034d53ad31.png)).
    * Questo creerà una utenza di esempio che può essere usata per coadivare lo sviluppo, con le seguenti informazioni (e credenziali)
        * Nome: Douglas Adams
        * Delega: Presidente presso il Comitato di Gaia
        * Email di accesso: `supporto@gaia.cri.it`
        * Password: `42`
8. **Avvia Jorvik** direttamente da PyCharm, scegliendo la configurazione `[jorvik] runserver`  ([Vedi immagine](https://user-images.githubusercontent.com/621062/39448999-c4bb7c40-4cbe-11e8-86be-4ba906ddc3ba.png)). Questo avvierà tutti i servizi necessari, utilizzando Docker Compose:
    * `web`: Un server di sviluppo Django (`runserver`), che rileverà automaticamente le modifiche al codice e si riavvierà automaticamente;
    * `db`: Un server di database PostgreSQL;
    * `broker`, `celery`: Un broker (Redis) e un server per lo smistamento della coda di task (ad es., task di smistamento della posta);
    * `pdf`: Un server per la generazione dei file PDF (Apache, PHP con DOMPDF);
    * `selenium`: Un server Selenium con Firefox e un server VNC, per l'esecuzione dei test funzionali.

#### Altri strumenti di sviluppo

* **Avvia i task periodici** (cronjob) direttamente da Pycharm, scegliendo la configurazione `[jorvik] runcrons`.
* **Esegui i test** (unitari e funzionali), scegliendo la configurazione `[jorvik] test` ([Vedi imagine](https://user-images.githubusercontent.com/621062/39449730-cbc0456e-4cc0-11e8-8b81-2fed10b9a028.png)).
* **Connettiti al database** PostgreSQL utilizzando gli strumenti di PyCharm ([Vedi immagine](https://user-images.githubusercontent.com/621062/39449692-b3264c4c-4cc0-11e8-951f-53db3a4a1648.png)):
  * Crea una nuove sorgente dati di tipo `PostgreSQL`,
  * Scegli `localhost` come host e `5432` come porta,
  * Utilizza `postgres` come username, senza alcuna password.
* **Connettiti in desktop remoto per osservare l'esecuzione dei test funzionali** con Selenium, che vengono eseguiti in una istanza di Firefox.
  * Utilizza il tuo client VNC preferito. Per esempio, su Linux, puoi usare `remmina`.
  * Crea una connessione VNC, usando `localhost` come host, e porta `5900`.
  * Se richiesto, utilizza `secret` come password.

#### Docker Compose

Se non utilizzi PyCharm, puoi utilizzare direttamente `docker-compose` da terminale
per orchestrare i container dei vari servizi di Jorvik. Ecco un paio di comandi di
esmepio.

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

### Autenticazione a due fattori (2FA)

Attualmente la piattaforma supporta la 2FA con:

 * Google Authenticator (e sistemi simili di OTP via QR Code)
 * Yubikey
 
Per l'utilizzo di Yubikey, vedi la documentazione del modulo al seguente indirizzo:
http://django-two-factor-auth.readthedocs.io/en/stable/installation.html#yubikey-setup

#### Attivare 2FA

 1. Installare Google Authenticator sul proprio dispositivo mobile
 2.  Fare il login normalmente nel pannello admin (`/admin`)
 3. Selezionare la voce "Two factor auth" nel menù admin
 4. Seguire le istruzioni dello wizard
 5. Selezionare "Token generator" fra le opzioni
 6. Scansionare con Google Authenticator il codice QR mostrato
 7. Inserire il token generato da Google Authenticator
 8. Il dispositivo è adesso configurato.
 