# Gaia Jovik

Jorvik e' il nome in codice del progetto di ridisegno del software del **Progetto Gaia** Croce Rossa Italiana
([GitHub](https://github.com/CroceRossaCatania/gaia), [Web](https://gaia.cri.it)).

I punti chiave nella riprogettazione sono i seguenti:
* Raccogliere il feedback ottenuto tramite <feedback@gaia.cri.it>,
* Raccogliere le necessita' espresse dagli utenti tramite il Supporto,
* Raccogliere le nuove necessita' dell'Associazione,

## Sviluppo

### Integrazione continua

Jorvik viene installato e testato sulle recenti versioni di Python 3, in modo automatico, da Travis CI ad ogni push.

Stato attuale di `master`: [![Build Status](https://travis-ci.org/CroceRossaItaliana/jorvik.svg?branch=master)](https://travis-ci.org/CroceRossaItaliana/jorvik)

### Requisiti

* Python 3 (es. `python3`)
* PIP 3 (es. `pip3`)
* MySQL 5.5+ (o MariaDB 10)
* [GEOS](http://trac.osgeo.org/geos/)

```bash
# Ubuntu 14.10+ (installa i Requisiti sopra indicati)
sudo apt-get install git python3-pip mysql-server binutils libproj-dev gdal-bin python3-dev libmysqlclient-dev
```

### Installazione

```bash
git clone https://github.com/CroceRossaItaliana/jorvik
cd jorvik
sudo pip3 install -r requirements.txt
```

### Configurazione

1. Modifica `config/mysql.cnf` con le credenziali di MySQL (non necessario se root pwd. vuota)
2. Crea il database con es. `mysql -u root -p -e 'CREATE DATABASE jorvik CHARSET utf8;'`
3. Esegui `python3 ./manage.py syncdb` per creare le tabelle del database
4. Esegui `python3 ./manage.py collectstatic` per creare la cartella `assets/`
5. **Avvia il server** con `python3 ./manage.py runserver`

