# Gaia Jovik

Jorvik è il nome in codice del progetto di ridisegno del software del **Progetto Gaia** Croce Rossa Italiana
([GitHub](https://github.com/CroceRossaCatania/gaia), [Web](https://gaia.cri.it)).


I punti chiave nella riprogettazione sono i seguenti:
* Raccogliere il feedback ottenuto tramite <feedback@gaia.cri.it>,
* Raccogliere le necessità espresse dagli utenti tramite il Supporto,
* Raccogliere le nuove necessità dell'Associazione,

## Segnalazioni tecniche / Issues

Le segnalazioni sono state spostate da GitHub al [**nuovo sistema di tracciamento issues**](https://jira.sviluppo-gaia.ovh/issues) utilizzato dal Progetto Gaia (JIRA). Vedi l'articolo "[Segnalazioni tecniche](https://github.com/CroceRossaItaliana/jorvik/wiki/Segnalazioni-tecniche)" sul wiki per maggiori informazioni sul come utilizzarlo.


## Sviluppo

Sei interessato a partecipare allo sviluppo di Gaia/Jorvik? Contattaci all'indirizzo e-mail <sviluppo@gaia.cri.it>!

### Integrazione continua

Jorvik viene installato e testato sulle recenti versioni di Python 3, in modo automatico, da Travis CI ad ogni push.

* Stato attuale di `master` (sviluppo): [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=master)](https://travis-ci.org/CroceRossaItaliana/jorvik)
* Stato attuale di `produzione` (online*): [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=produzione)](https://travis-ci.org/CroceRossaItaliana/jorvik)

\*: *Il deployment non viene ancora effettuato automaticamente.*


### Ambienti di sviluppo e staging

| Nome            | Link                                              | Branch              | Stato CI                                                                                                                                         | Destinazione d'uso              | Auto update |
|-----------------|---------------------------------------------------|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------|-------------|
| **`leia`**      | [URL](http://leia.staging.sviluppo-gaia.ovh)      | `staging-leia`      | [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=staging-leia)](https://travis-ci.org/CroceRossaItaliana/jorvik)      | Staging, pre-produzione         | Sì          |
| **`hansolo`**   | [URL](http://hansolo.staging.sviluppo-gaia.ovh)   | `staging-hansolo`   | [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=staging-hansolo)](https://travis-ci.org/CroceRossaItaliana/jorvik)   | Supporto, formazione supporto   | Sì          |
| **`luke`**      | [URL](http://luke.staging.sviluppo-gaia.ovh)      | `staging-luke`      | [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=staging-luke)](https://travis-ci.org/CroceRossaItaliana/jorvik)      | Testing, QA                     | Sì          |
| **`chewbacca`** | [URL](http://chewbacca.staging.sviluppo-gaia.ovh) | `staging-chewbacca` | [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=staging-chewbacca)](https://travis-ci.org/CroceRossaItaliana/jorvik) | Sviluppo, pre-staging           | Sì          |
| **`obiwan`**    | [URL](http://obiwan.staging.sviluppo-gaia.ovh)    | `staging-obiwan`    | [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=staging-obiwan)](https://travis-ci.org/CroceRossaItaliana/jorvik)    | Eventi di formazione, supporter | Sì          |


* Gli ambienti di sviluppo e staging sono ospitati presso la macchina dedicata per la squadra di supporto e sviluppo (`sviluppo-gaia.ovh`),
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

Per la configurazione automatica dell'ambiente di sviluppo su **Linux, Mac OS X 10.9+ e Windows 8+**, è possibile usare Vagrant con VirtualBox. Vagrant gestisce la creazione e la configurazione automatica (provisioning) di una macchina virtuale.

1. **Scarica Jorvik** usando Git ([GitHub Desktop](https://desktop.github.com/) per Windows e Mac OS X, o da terminale come segue)

    ```bash
    git clone --recursive https://github.com/CroceRossaItaliana/jorvik
    ```

1. **Aprire un terminale** (prompt dei Comandi su Windows) e accedere alla cartella dove risiede il codice appena scaricato.

   ```bash
   cd jorvik
   ```

1. **Scarica VirtualBox** da [virtualbox.org](https://www.virtualbox.org/wiki/Downloads),
2. **Scarica Vagrant** da [vagrantup.com](https://www.vagrantup.com/downloads.html),
3. **Configura la macchina virtuale** (potrebbe volerci un po')

    ```bash
    vagrant up --provision
    ```

4. **Crea il primo utente** (amministratore)

    ```bash
    vagrant ssh
    cd /vagrant
    python3 manage.py syncdb
    ```

5. **Installare PyCharm Professional** da [JetBrains](https://www.jetbrains.com/pycharm/). La licenza e' gratis per gli studenti. Contattaci se necessiti di una licenza per lavorare su Jorvik: abbiamo un numero limitato di licenze, quindi approfitta del trial di 30 giorni per assicurarti di voler collaborare.
6. **Configurare PyCharm per usare Vagrant**:
  * Preferenze > Progetto > Interprete > Aggiungi interprete remoto
    ![image](https://cloud.githubusercontent.com/assets/621062/10762277/4da18088-7cbd-11e5-924e-a2737d7783e1.png)

  * Scegliere **"Vagrant"** e **`/usr/bin/python3`** come interprete, e cliccare OK
    ![image](https://cloud.githubusercontent.com/assets/621062/10762319/7ce52214-7cbd-11e5-8cbf-26bfe0565b7e.png)

    **Nota bene**: Su Mac OS X, se questo step fallisce ("impossibile trovare vagrant"), e' per via di un bug noto con la piattaforma. In tal caso e' necessario chiudere e riavviare PyChar da Terminale, con il comando `charm`.

  * Assicurarsi che l'interprete "Vagrant" sia ora selezionato come predefinito per il progetto, quindi cliccare OK

6. **Usare il tasto "Run" su PyCharm** per controllare e avviare il server
  ![image](https://cloud.githubusercontent.com/assets/621062/10762357/abcb3050-7cbd-11e5-9fdf-c08a0b439369.png)


#### Vagrant

* **Configurare (primo avvio) e avviare la macchina virtuale**

    ```bash
    vagrant up
    ```

* **Spegnere la macchina virtuale**

    ```bash
    vagrant halt -f
    ```

* **Cancellare e riconfigurare la macchina virtuale**

    ```bash
    vagrant halt -f && vagrant destroy -f && vagrant up
    ```

* **Collegarsi in SSH alla macchina virtuale** (se necessario)

    ```bash
    vagrant ssh
    cd vagrant/ # Directory con jorvik
    ```
    
[JetBrains PyCharm](https://www.jetbrains.com/pycharm/) racchiude gli strumenti Django in un buon IDE.

### 2 Factor authentication

Attualmente la piattaforma supporta la 2FA con:

 * Google Authenticator (e sistemi simili di OTP via QR Code)
 * Yubikey
 
Per il setup di Yubikey si veda: http://django-two-factor-auth.readthedocs.io/en/stable/installation.html#yubikey-setup

Per attivare la 2FA per un utente è sufficiente:

 * Installare Google Authenticator sul proprio dispositivo mobile
 * Fare il login normalmente nell'admin
 * Selezionare la voce "Two factor auth" nel menù admin
 * Seguire le istruzioni dello wizard
 * Selezionare "Token generator" fra le opzioni
 * Scansionare con Google Authenticator il codice QR mostrato
 * Inserire il token generato da Google Authenticator
 * Il dispositivo è adesso autenticato
 
