# Gaia Jovik

Jorvik è il nome in codice del progetto di ridisegno del software del **Progetto Gaia** Croce Rossa Italiana
([GitHub](https://github.com/CroceRossaCatania/gaia), [Web](https://gaia.cri.it)).

I punti chiave nella riprogettazione sono i seguenti:
* Raccogliere il feedback ottenuto tramite <feedback@gaia.cri.it>,
* Raccogliere le necessità espresse dagli utenti tramite il Supporto,
* Raccogliere le nuove necessità dell'Associazione,

## Sviluppo

Sei interessato a partecipare allo sviluppo di Gaia/Jorvik? Contattaci all'indirizzo e-mail <sviluppo@gaia.cri.it>!

### Integrazione continua

Jorvik viene installato e testato sulle recenti versioni di Python 2 e 3, in modo automatico, da Travis CI ad ogni push.

Stato attuale di `master`: [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=master)](https://travis-ci.org/CroceRossaItaliana/jorvik)

### Documentazione

Puoi trovare la **[Documentazione sul Wiki del progetto](https://github.com/CroceRossaItaliana/jorvik/wiki)**.

### Requisiti

* **[Python 2.7-3.x](https://www.python.org/downloads/)** (es. `python3`)
* **[PIP 2 o 3](https://www.python.org/downloads/)** (es. `pip3`)
* **[PostgreSQL](http://www.postgresql.org/) 9.4+** con [PostGIS](http://postgis.net/))
* **[GEOS](http://trac.osgeo.org/geos/)** (Geometry Engine Open Source)
* **Linux**, Mac OS X e, probabilmente, Windows Server 2008 o 7 e superiori

### Ambiente di sviluppo

Per la configurazione automatica dell'ambiente di sviluppo su **Linux e Mac OS X 10.9+**, è possibile usare Vagrant.
Vagrant gestisce la creazione e la configurazione automatica (provisioning) di una macchina virtuale.

1. **Scarica Jorvik** usando git

    ```bash
    git clone --recursive https://github.com/CroceRossaItaliana/jorvik
    cd jorvik
    ```

1. **Scarica VirtualBox** da [virtualbox.org](https://www.virtualbox.org/wiki/Downloads),
2. **Scarica Vagrant** da [vagrantup.com](https://www.vagrantup.com/downloads.html),
3. **Configura la macchina virtuale** (potrebbe volerci un po')

    ```bash
    vagrant up
    ```

4. **Crea il primo utente** (amministratore)

    ```bash
    vagrant ssh
    cd /vagrant
    python3 manage.py syncdb
    ```

5. **Installare PyCharm** [JetBrains PyCharm](https://www.jetbrains.com/pycharm/)
6. **Configurare PyCharm per usare Vagrant**:
  * Preferenze > Progetto > Interprete > Aggiungi interprete remoto
    ![image](https://cloud.githubusercontent.com/assets/621062/10762277/4da18088-7cbd-11e5-924e-a2737d7783e1.png)

  * Scegliere "Vagrant" e `/usr/bin/python3` come interprete, e cliccare OK
    ![image](https://cloud.githubusercontent.com/assets/621062/10762319/7ce52214-7cbd-11e5-8cbf-26bfe0565b7e.png)
  
  * Assicurarsi che l'interprete "Vagrant" sia ora selezionato, quindi cliccare OK
  
6. **Usare il tasto "Run" su PyCharm** per controllare e avviare il server
  ![image](https://cloud.githubusercontent.com/assets/621062/10762357/abcb3050-7cbd-11e5-9fdf-c08a0b439369.png)


#### Vagrant

* **Configurare (primo avvio) e avviare la macchina virtuale**

    ```bash
    vagrant up
    ```

* **Spegnere la macchina virtuale**

    ```bash
    vagrant halt
    ```

* **Cancellare e riconfigurare la macchina virtuale**

    ```bash
    vagrant halt && vagrant destroy && vagrant up
    ```

* **Collegarsi in SSH alla macchina virtuale** (se necessario)

    ```bash
    vagrant ssh
    cd vagrant/ # Directory con jorvik
    ```




[JetBrains PyCharm](https://www.jetbrains.com/pycharm/) racchiude gli strumenti Django in un buon IDE.
