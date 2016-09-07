import datetime
from datetime import timedelta
from unittest import skip
from django.utils import timezone
from django.test import TestCase

from attivita.forms import ModuloOrganizzaAttivitaReferente
from attivita.models import Attivita, Area, Turno
from anagrafica.costanti import LOCALE 
from anagrafica.models import Sede, Persona, Appartenenza, Delega
from anagrafica.permessi.applicazioni import REFERENTE, PRESIDENTE, DELEGATO_CO
from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_persona, crea_persona_sede_appartenenza, crea_area_attivita, crea_turno


class TestAttivita(TestCase):
    def test_attivita(self):

        ##Sicilia -> [Fiumefreddo, Mascali]
        ##Calabria ->[]

        sicilia = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        sicilia.save()

        fiumefreddo = Sede(
            nome="Comitato Locale di Fiumefreddo di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        fiumefreddo.save()

        mascali = Sede(
            nome="Comitato Locale di Mascali",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        mascali.save()

        calabria = Sede(
            nome="Comitato Regionale di Calabria",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        calabria.save()

        area = Area(
            nome="6",
            obiettivo=6,
            sede=sicilia,
        )
        area.save()

        a = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=sicilia,
            estensione=sicilia,
        )
        a.save()

        a1 = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=fiumefreddo,
            estensione=sicilia,
        )
        a1.save()

        t = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30),
            minimo=1,
            massimo=6,
        )
        t.save()

        t1 = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 10, 10),
            fine=datetime.datetime(2015, 10, 30)
        )
        t1.save()

        t2 = Turno(
            attivita=a1,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30)
        )
        t2.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        p1 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIRAJDO",
            data_nascita="1994-2-5"
        )
        p1.save()

        p2 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJDO",
            data_nascita="1994-2-5"
        )
        p2.save()

        p3 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJMI",
            data_nascita="1994-2-5"
        )
        p3.save()

        app = Appartenenza(
            persona=p,
            sede=sicilia,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app.save()

        app1 = Appartenenza(
            persona=p1,
            sede=fiumefreddo,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app1.save()

        app2 = Appartenenza(
            persona=p2,
            sede=mascali,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app2.save()

        app3 = Appartenenza(
            persona=p3,
            sede=calabria,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app3.save()

        self.assertTrue(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t.pk).exists(),
            msg="Il turno viene trovato nel calendario - attivita' creata dalla sede del volontario"
        )

        self.assertFalse(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t1.pk).exists(),
            msg="Il turno non viene trovato nel calendario - attivita' creata dalla sede del volontario"
        )


    def test_attivita_estesa(self):

        sicilia = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        sicilia.save()

        fiumefreddo = Sede(
            nome="Comitato Locale di Fiumefreddo di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        fiumefreddo.save()

        mascali = Sede(
            nome="Comitato Locale di Mascali",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        mascali.save()

        calabria = Sede(
            nome="Comitato Regionale di Calabria",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        calabria.save()

        area = Area(
            nome="6",
            obiettivo=6,
            sede=sicilia,
        )
        area.save()

        a = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=sicilia,
            estensione=sicilia,
        )
        a.save()

        a1 = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=fiumefreddo,
            estensione=sicilia,
        )
        a1.save()

        t = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30),
            minimo=1,
            massimo=6,
        )
        t.save()

        t1 = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 10, 10),
            fine=datetime.datetime(2015, 10, 30)
        )
        t1.save()

        t2 = Turno(
            attivita=a1,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30)
        )
        t2.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        p1 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIRAJDO",
            data_nascita="1994-2-5"
        )
        p1.save()

        p2 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJDO",
            data_nascita="1994-2-5"
        )
        p2.save()

        p3 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJMI",
            data_nascita="1994-2-5"
        )
        p3.save()

        app = Appartenenza(
            persona=p,
            sede=sicilia,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app.save()

        app1 = Appartenenza(
            persona=p1,
            sede=fiumefreddo,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app1.save()

        app2 = Appartenenza(
            persona=p2,
            sede=mascali,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app2.save()

        app3 = Appartenenza(
            persona=p3,
            sede=calabria,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app3.save()

        self.assertTrue(
            p2.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t2.pk).exists(),
            msg="Il turno viene trovato nel calendario - attivita' estesa al volontario"
        )

        self.assertFalse(
            p3.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t2.pk).exists(),
            msg="Il turno non viene trovato nel calendario - attivita' estesa al volontario"
        )

    def test_permessi_attivita(self):

        fiumefreddo = Sede(
            nome="Comitato Locale di Fiumefreddo di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        fiumefreddo.save()

        mascali = Sede(
            nome="Comitato Locale di Mascali",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        mascali.save()

        area = Area(
            nome="6",
            obiettivo=6,
            sede=fiumefreddo,
        )
        area.save()

        a = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=mascali,
        )
        a.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJMI",
            data_nascita="1994-2-5"
        )
        p.save()

        app = Appartenenza(
            persona=p,
            sede=fiumefreddo,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app.save()

        t = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30),
            minimo=1,
            massimo=6,
        )
        t.save()

        delega = Delega(
            oggetto=a,
            persona=p,
            tipo=REFERENTE,
            inizio="2015-11-15",
        )
        delega.save()

        self.assertTrue(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t.pk).exists(),
            msg="Il turno viene trovato nel calendario - attivita' creata dalla sede del volontario"
        )


class TestFunzionaleAttivita(TestFunzionale):

    def test_crea_area(self):

        presidente = crea_persona()
        persona, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sessione_presidente = self.sessione_utente(persona=presidente)
        #sessione_persona = self.sessione_utente(persona=persona)

        # Crea area di intervento
        sessione_presidente.click_link_by_partial_text("Attività")
        sessione_presidente.click_link_by_partial_text("Aree di intervento")
        sessione_presidente.click_link_by_partial_text(sede.nome)
        sessione_presidente.fill('nome', "Area 42")
        sessione_presidente.fill('obiettivo', '6')
        sessione_presidente.find_by_xpath("//button[@type='submit']").first.click()

        # Nomina la persona come responsabile
        self.seleziona_delegato(sessione_presidente, persona)

        self.assertTrue(
            sessione_presidente.is_text_present("Area 42"),
            "La nuova area è stata creata con successo",
        )

        self.assertTrue(
            sessione_presidente.is_text_present(persona.nome_completo),
            "La nuova area ha il responsabile assegnato",
        )

        self.assertTrue(
            sessione_presidente.is_text_present("0 attività"),
            "La nuova area non ha alcuna attività",
        )

    def test_crea_attivita(self):

        presidente = crea_persona()
        persona, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        area = Area(sede=sede, nome="Area 42", obiettivo=6)
        area.save()

        # Crea le sessioni
        sessione_presidente = self.sessione_utente(persona=presidente)
        sessione_persona = self.sessione_utente(persona=persona)

        # Presidente: Vai a organizza attivita
        sessione_presidente.click_link_by_partial_text("Attività")
        sessione_presidente.click_link_by_partial_text("Organizza attività")

        # Presidente: Riempi dettagli attivita
        sessione_presidente.fill('nome', "Fine del mondo")
        sessione_presidente.select('area', area.pk)
        sessione_presidente.select('scelta', ModuloOrganizzaAttivitaReferente.SONO_IO)

        # Presidente: Invia il modulo
        sessione_presidente.find_by_xpath("//button[@type='submit']").first.click()

        # Presidente: Torna all'elenco attività, naviga fino a nuovo turno.
        sessione_presidente.click_link_by_partial_text("Gestione turni")
        sessione_presidente.click_link_by_partial_text("Crea nuovo turno")

        inizio = (timezone.now()).strftime("%d/%m/%Y %H:%m")
        fine = (timezone.now() + timedelta(hours=30)).strftime("%d/%m/%Y %H:%m")

        # Presidente: Riempi i dettagli del nuovo turno
        sessione_presidente.fill('nome', "Vedetta")
        sessione_presidente.fill('inizio', inizio)
        sessione_presidente.fill('fine', fine)
        sessione_presidente.fill('minimo', 1)
        sessione_presidente.fill('massimo', 5)
        sessione_presidente.fill('prenotazione', inizio)

        # Presidente: Invia il modulo
        sessione_presidente.find_by_xpath("//button[@type='submit']").first.click()

        # Volontario: Vai in attività
        sessione_persona.click_link_by_partial_text("Attività")

        self.assertFalse(sessione_persona.is_text_present("Vedetta"),
                         msg="L'attività non è visibile.")

        # Presidente: Modifica attività
        sessione_presidente.click_link_by_partial_text("Elenco attività")
        sessione_presidente.click_link_by_partial_text("modifica info")
        sessione_presidente.click_link_by_partial_text("Gestione attività")

        # Presidente: Imposta stato come VISIBILE
        sessione_presidente.select('stato', Attivita.VISIBILE)

        # Presidente: Invia il modulo
        sessione_presidente.find_by_xpath("//button[@type='submit']").first.click()

        # Volontario: Vai in attività
        sessione_persona.click_link_by_partial_text("Attività")

        self.assertTrue(sessione_persona.is_text_present("Vedetta"),
                        msg="L'attività è ora visibile.")

        # Volontario: Clicca sul turno
        sessione_persona.click_link_by_partial_text("Vedetta")

        self.assertTrue(sessione_persona.is_text_present("Scoperto!"),
                        msg="Viene mostrata correttamente come scoperta.")

    def test_richiesta_partecipazione(self):

        referente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        area, attivita = crea_area_attivita(sede=sede)
        inizio = timezone.now() + timedelta(hours=12)
        fine = inizio + timedelta(hours=2)

        turno = crea_turno(attivita, inizio=inizio, fine=fine)

        attivita.aggiungi_delegato(REFERENTE, referente)

        # Crea le sessioni
        sessione_referente = self.sessione_utente(persona=referente)
        sessione_volontario = self.sessione_utente(persona=volontario)

        # Volontario: Apri la pagina dell'attivita'
        sessione_volontario.visit("%s%s" % (self.live_server_url, attivita.url))

        # Volontario: Apri pagina turni
        sessione_volontario.click_link_by_partial_text("Turni")

        # Volontario: Chiedi di partecipare
        sessione_volontario.click_link_by_partial_text("Partecipa")

        self.assertTrue(sessione_volontario.is_text_present("Richiesta inoltrata"),
                        msg="La richiesta e stata inoltrata")

        # Volontario: Apri la pagina dell'attivita', pagina turni
        sessione_volontario.visit("%s%s" % (self.live_server_url, attivita.url))
        sessione_volontario.click_link_by_partial_text("Turni")

        self.assertTrue(sessione_volontario.is_text_present("Hai chiesto di partecipare"),
                        msg="Utente ha feedback sull'aver chiesto di partecipare")

        # Volontario: Vai allo storico
        sessione_volontario.click_link_by_partial_text("Miei turni")

        self.assertTrue(sessione_volontario.is_text_present("In attesa"),
                        msg="Storico mostra stato in attesa della richiesta")

        # Referente: Trova la richiesta
        sessione_referente.click_link_by_partial_text("Richieste")

        self.assertTrue(sessione_referente.is_text_present(volontario.nome_completo),
                        msg="La richiesta mostra il nome del volontario")

        self.assertTrue(sessione_referente.is_text_present(turno.nome),
                        msg="La richiesta mostra il nome del turno")

        # Referente: Trova la richiesta
        sessione_referente.click_link_by_partial_text("Conferma")

        # Volontario: Vai allo storico
        sessione_volontario.click_link_by_partial_text("Miei turni")

        self.assertTrue(sessione_volontario.is_text_present("Approvata"),
                        msg="La richiesta risulta ora approvata")

        # Volontario: Vai al turno
        sessione_volontario.click_link_by_partial_text(turno.nome)

        self.assertTrue(sessione_volontario.is_text_present("Partecipazione confermata"),
                        msg="La partecipazione risulta nel turno")

    def test_campo_centrale_operativa_disabilitata(self):
 
        presidente = crea_persona()
        referente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()

        delega = Delega(
            oggetto=sede,
            persona=presidente,
            tipo=PRESIDENTE,
            inizio="2005-11-15",
        )
        delega.save()

        delega_2 = Delega(
            oggetto=sede,
            persona=referente,
            tipo=DELEGATO_CO,
            inizio="2005-11-15",
        )
        delega_2.save()

        area, attivita = crea_area_attivita(sede=sede)
        inizio = timezone.now() + timedelta(hours=12)
        fine = inizio + timedelta(hours=2)

        turno = crea_turno(attivita, inizio=inizio, fine=fine)

        attivita.aggiungi_delegato(REFERENTE, volontario)
        attivita.aggiungi_delegato(REFERENTE, referente)


        # Crea le sessioni
        sessione_referente = self.sessione_utente(persona=referente)
        sessione_volontario = self.sessione_utente(persona=volontario)
        sessione_presidente = self.sessione_utente(persona=presidente)

        # Volontario: Apri la pagina dell'attivita'
        sessione_volontario.visit("%s%smodifica/" % (self.live_server_url, attivita.url))
        self.assertIn('disabled', sessione_volontario.find_by_id('id_centrale_operativa')[0].outer_html)

        sessione_presidente.visit("%s%smodifica/" % (self.live_server_url, attivita.url))
        self.assertNotIn('disabled', sessione_presidente.find_by_id('id_centrale_operativa')[0].outer_html)

        sessione_referente.visit("%s%smodifica/" % (self.live_server_url, attivita.url))
        self.assertNotIn('disabled', sessione_referente.find_by_id('id_centrale_operativa')[0].outer_html)
