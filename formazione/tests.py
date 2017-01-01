import os
import re

from datetime import timedelta
from unittest import skipIf

from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from anagrafica.models import Appartenenza
from autenticazione.utils_test import TestFunzionale
from base.geo import Locazione
from base.models import Autorizzazione
from base.utils import poco_fa
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, email_fittizzia, codice_fiscale, crea_utenza
from jorvik.settings import GOOGLE_KEY
from .models import CorsoBase, Aspirante, InvitoCorsoBase


class TestCorsi(TestCase):
    def test_invito_aspirante(self):
        presidente = crea_persona()
        presidente.email_contatto = email_fittizzia()
        presidente.save()
        crea_utenza(presidente, presidente.email_contatto)
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        aspirante1 = crea_persona()
        aspirante1.email_contatto = email_fittizzia()
        aspirante1.codice_fiscale = codice_fiscale()
        aspirante1.save()
        a = Aspirante(persona=aspirante1)
        a.locazione = sede.locazione
        a.save()

        oggi = poco_fa()
        corso = CorsoBase.objects.create(
            stato=CorsoBase.ATTIVO,
            sede=sede,
            data_inizio=oggi + timedelta(days=7),
            data_esame=oggi + timedelta(days=14),
            progressivo=1,
            anno=oggi.year,
            descrizione='Un corso',
        )
        self.assertFalse(aspirante1.autorizzazioni_in_attesa().exists())

        p = InvitoCorsoBase(persona=aspirante1, corso=corso, invitante=presidente)
        p.save()
        p.richiedi()
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find("Richiesta di iscrizione a Corso Base da {}".format(presidente.nome_completo)) > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(aspirante1.email_contatto, email.to)

        self.assertEqual(aspirante1.autorizzazioni_in_attesa().count(), 1)
        aspirante1.autorizzazioni_in_attesa()[0].concedi()
        self.assertEqual(len(mail.outbox), 3)
        email_aspirante = False
        email_presidente = False
        for email in mail.outbox[1:]:
            if aspirante1.email_contatto in email.to:
                email_aspirante = True
                self.assertTrue(email.subject.find('Iscrizione a Corso Base') > -1)
            elif presidente.email_contatto in email.to:
                email_presidente = True
                self.assertTrue(email.subject.find('Richiesta di iscrizione a Corso Base APPROVATA') > -1)
            else:
                raise AssertionError('Email a destinatario sconosciuto {}'.format(email.to))
        self.assertTrue(email_aspirante)
        self.assertTrue(email_presidente)

        self.assertFalse(aspirante1.autorizzazioni_in_attesa().exists())
        self.assertFalse(corso.inviti.exists())
        self.assertEqual(corso.partecipazioni.count(), 1)

    def test_invito_aspirante_automatico(self):
        presidente = crea_persona()
        presidente.email_contatto = email_fittizzia()
        presidente.save()
        crea_utenza(presidente, presidente.email_contatto)
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        aspirante1 = crea_persona()
        aspirante1.email_contatto = email_fittizzia()
        aspirante1.codice_fiscale = codice_fiscale()
        aspirante1.save()
        a = Aspirante(persona=aspirante1)
        a.locazione = sede.locazione
        a.save()

        oggi = poco_fa()
        corso = CorsoBase.objects.create(
            stato=CorsoBase.ATTIVO,
            sede=sede,
            data_inizio=oggi + timedelta(days=7),
            data_esame=oggi + timedelta(days=14),
            progressivo=1,
            anno=oggi.year,
            descrizione='Un corso',
        )
        self.assertFalse(aspirante1.autorizzazioni_in_attesa().exists())

        partecipazione = InvitoCorsoBase(persona=aspirante1, corso=corso, invitante=presidente)
        partecipazione.save()
        partecipazione.richiedi()

        self.assertFalse(InvitoCorsoBase.con_esito_no().exists())
        autorizzazione = presidente.autorizzazioni_richieste.first()
        autorizzazione.scadenza = timezone.now() - timedelta(days=10)
        autorizzazione.save()
        self.assertFalse(autorizzazione.concessa)
        Autorizzazione.gestisci_automatiche()
        self.assertEqual(len(mail.outbox), 2)
        messaggio = mail.outbox[1]
        self.assertTrue(messaggio.subject.find('Richiesta di iscrizione a Corso Base RESPINTA') > -1)
        self.assertFalse(messaggio.subject.find('Richiesta di iscrizione a Corso Base APPROVATA') > -1)
        self.assertTrue(messaggio.body.find('una tua richiesta &egrave; rimasta in attesa per 30 giorni e come da policy') == -1)
        self.assertEqual(autorizzazione.concessa, None)
        self.assertTrue(InvitoCorsoBase.con_esito_no().exists())

    def test_corso_pubblico(self):
        """
        Un corso è visibile fino a FORMAZIONE_FINESTRA_CORSI_INIZIATI giorni dal suo inizio
        """
        presidente = crea_persona()
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        oggi = poco_fa()

        corso = CorsoBase.objects.create(
            stato=CorsoBase.ATTIVO,
            sede=sede,
            data_inizio=oggi + timedelta(days=7),
            data_esame=oggi + timedelta(days=14),
            progressivo=1,
            anno=oggi.year,
            descrizione='Un corso',
        )
        self.assertTrue(CorsoBase.pubblici().exists())
        self.assertFalse(corso.iniziato)
        self.assertFalse(corso.troppo_tardi_per_iscriverti)
        self.assertTrue(corso.possibile_aggiungere_iscritti)
        corso.data_inizio = oggi - timedelta(days=(settings.FORMAZIONE_FINESTRA_CORSI_INIZIATI - 1))
        corso.save()
        self.assertTrue(corso.iniziato)
        self.assertFalse(corso.troppo_tardi_per_iscriverti)
        self.assertTrue(corso.possibile_aggiungere_iscritti)
        self.assertTrue(CorsoBase.pubblici().exists())

        corso.data_inizio = oggi - timedelta(days=settings.FORMAZIONE_FINESTRA_CORSI_INIZIATI)
        corso.save()
        self.assertTrue(corso.iniziato)
        self.assertTrue(corso.troppo_tardi_per_iscriverti)
        self.assertTrue(corso.possibile_aggiungere_iscritti)
        self.assertFalse(CorsoBase.pubblici().exists())

    def test_autocomplete_sostentitore_aspirante(self):
        direttore, sede, appartenenza = crea_persona_sede_appartenenza()
        aspirante1 = crea_persona()
        aspirante1.email_contatto = email_fittizzia()
        aspirante1.codice_fiscale = codice_fiscale()
        a = Aspirante(persona=aspirante1)
        a.locazione = sede.locazione
        a.save()
        aspirante1.save()

        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante1.codice_fiscale[:3]))
        self.assertContains(response, aspirante1.nome_completo)

        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante1.nome_completo))
        self.assertNotContains(response, aspirante1.nome_completo)

        # Creiamo aspirante
        aspirante2 = crea_persona()
        aspirante2.email_contatto = email_fittizzia()
        aspirante2.codice_fiscale = codice_fiscale()
        a = Aspirante(persona=aspirante2)
        a.locazione = sede.locazione
        a.save()
        aspirante2.save()

        # Se è solo aspirante viene selezionato
        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante1.codice_fiscale[:3]))
        self.assertContains(response, aspirante1.nome_completo)

        Appartenenza.objects.create(
            persona=aspirante2,
            sede=sede,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )

        # Con un appartenenza come volontario non è più selezionabile
        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante2.codice_fiscale[:3]))
        self.assertNotContains(response, aspirante2.nome_completo)

        # Dimettiamolo
        aspirante2.espelli()
        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante2.codice_fiscale[:3]))
        self.assertContains(response, aspirante2.nome_completo)

        # Reintegriamolo
        Appartenenza.objects.create(
            persona=aspirante2,
            sede=sede,
            membro=Appartenenza.VOLONTARIO,
            inizio=poco_fa(),
        )
        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante2.codice_fiscale[:3]))
        self.assertNotContains(response, aspirante2.nome_completo)

    def test_aggiungi_aspirante_multiplo(self):
        presidente = crea_persona()
        presidente.email_contatto = email_fittizzia()
        presidente.save()
        crea_utenza(presidente, presidente.email_contatto)
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        aspirante1 = crea_persona()
        aspirante1.email_contatto = email_fittizzia()
        aspirante1.codice_fiscale = codice_fiscale()
        aspirante1.save()
        a = Aspirante(persona=aspirante1)
        a.locazione = sede.locazione
        a.save()

        oggi = poco_fa()
        corso = CorsoBase.objects.create(
            stato=CorsoBase.ATTIVO,
            sede=sede,
            data_inizio=oggi + timedelta(days=7),
            data_esame=oggi + timedelta(days=14),
            progressivo=1,
            anno=oggi.year,
            descrizione='Un corso',
        )

        self.client.login(username=presidente.email_contatto, password='prova')

        # Iscrizione aspirante
        iscritto = {
            'persone': [aspirante1.pk]
        }
        response = self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritto)
        self.assertEqual(corso.partecipazioni.count(), 0)
        self.assertEqual(corso.inviti.count(), 1)
        self.assertContains(response, aspirante1.nome_completo)
        self.assertContains(response, 'In attesa')
        # Correttezza email di invito
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(
            email.subject.find("Richiesta di iscrizione a Corso Base da {}".format(presidente.nome_completo)) > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(aspirante1.email_contatto, email.to)

        iscritto = {
            'persone': [aspirante1.pk]
        }
        response = self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritto)
        self.assertContains(response, 'Già invitato')

    def test_aggiungi_sostenitore_aspirante(self):
        presidente = crea_persona()
        presidente.email_contatto = email_fittizzia()
        presidente.save()
        crea_utenza(presidente, presidente.email_contatto)
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sostenitore = crea_persona()
        sostenitore.email_contatto = email_fittizzia()
        sostenitore.codice_fiscale = codice_fiscale()
        sostenitore.save()
        Appartenenza.objects.create(
            persona=sostenitore,
            sede=sede,
            membro=Appartenenza.SOSTENITORE,
            inizio="1980-12-10",
        )

        aspirante1 = crea_persona()
        aspirante1.email_contatto = email_fittizzia()
        aspirante1.codice_fiscale = codice_fiscale()
        aspirante1.save()
        a = Aspirante(persona=aspirante1)
        a.locazione = sede.locazione
        a.save()

        aspirante2 = crea_persona()
        aspirante2.email_contatto = email_fittizzia()
        aspirante2.codice_fiscale = codice_fiscale()
        aspirante2.save()
        a = Aspirante(persona=aspirante2)
        a.locazione = sede.locazione
        a.save()

        oggi = poco_fa()
        corso = CorsoBase.objects.create(
            stato=CorsoBase.ATTIVO,
            sede=sede,
            data_inizio=oggi + timedelta(days=7),
            data_esame=oggi + timedelta(days=14),
            progressivo=1,
            anno=oggi.year,
            descrizione='Un corso',
        )

        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante1.codice_fiscale[:3]))
        self.assertContains(response, aspirante1.nome_completo)

        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(aspirante2.codice_fiscale[:3]))
        self.assertContains(response, aspirante2.nome_completo)

        response = self.client.get('/autocomplete/IscrivibiliCorsiAutocompletamento/?q={}'.format(sostenitore.codice_fiscale[:3]))
        self.assertContains(response, sostenitore.nome_completo)

        self.client.login(username=presidente.email_contatto, password='prova')

        # Iscrizione aspirante
        iscritto = {
            'persone': [aspirante1.pk]
        }
        response = self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritto)
        self.assertEqual(corso.partecipazioni.count(), 0)
        self.assertEqual(corso.inviti.count(), 1)
        self.assertContains(response, aspirante1.nome_completo)
        self.assertContains(response, 'In attesa')
        # Correttezza email di invito
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find("Richiesta di iscrizione a Corso Base da {}".format(presidente.nome_completo)) > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(aspirante1.email_contatto, email.to)

        # Iscrizione aspirante
        iscritto = {
            'persone': [aspirante2.pk]
        }
        self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritto)
        self.assertEqual(corso.inviti.count(), 2)
        # Correttezza email di invito
        self.assertEqual(len(mail.outbox), 2)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find("Richiesta di iscrizione a Corso Base da {}".format(presidente.nome_completo)) > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(aspirante1.email_contatto, email.to)

        # Iscrizione sostenitore
        iscritto = {
            'persone': [sostenitore.pk]
        }
        response = self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritto)
        self.assertEqual(corso.partecipazioni.count(), 1)
        self.assertContains(response, 'Sì')
        self.assertContains(response, sostenitore.nome_completo)
        # Correttezza email di iscrizione
        self.assertEqual(len(mail.outbox), 3)
        email = mail.outbox[2]
        self.assertTrue(email.subject.find("Iscrizione a Corso Base") > -1)
        self.assertEqual(len(email.to), 1)
        self.assertIn(sostenitore.email_contatto, email.to)

        # Un aspirante approva
        self.assertEqual(corso.partecipazioni.count(), 1)
        self.assertEqual(aspirante1.autorizzazioni_in_attesa().count(), 1)
        aspirante1.autorizzazioni_in_attesa()[0].concedi()
        self.assertEqual(len(mail.outbox), 5)
        email_aspirante = False
        email_presidente = False
        for email in mail.outbox[3:]:
            if aspirante1.email_contatto in email.to:
                email_aspirante = True
                self.assertTrue(email.subject.find('Iscrizione a Corso Base') > -1)
            elif presidente.email_contatto in email.to:
                email_presidente = True
                self.assertTrue(email.subject.find('Richiesta di iscrizione a Corso Base APPROVATA') > -1)
            else:
                raise AssertionError('Email a destinatario sconosciuto')
        self.assertTrue(email_aspirante)
        self.assertTrue(email_presidente)
        self.assertFalse(aspirante1.autorizzazioni_in_attesa().exists())
        self.assertEqual(corso.inviti.count(), 1)
        self.assertEqual(corso.partecipazioni.count(), 2)

        # Un aspirante declina
        self.assertEqual(aspirante2.autorizzazioni_in_attesa().count(), 1)
        aspirante2.autorizzazioni_in_attesa()[0].nega()
        self.assertEqual(len(mail.outbox), 6)
        email = mail.outbox[5]
        self.assertIn(presidente.email_contatto, email.to)
        self.assertTrue(email.subject.find('Richiesta di iscrizione a Corso Base RESPINTA') > -1)
        self.assertFalse(aspirante2.autorizzazioni_in_attesa().exists())
        self.assertFalse(corso.inviti.exists())
        self.assertEqual(corso.partecipazioni.count(), 2)


class TestFunzionaleFormazione(TestFunzionale):
    """
    Questa classe raccoglie i test funzionali per la formazione
    in Gaia.
    """

    def test_gestione_inviti(self):

        presidente = crea_persona()
        presidente.email_contatto = email_fittizzia()
        presidente.save()
        crea_utenza(presidente, presidente.email_contatto)
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sostenitore = crea_persona()
        sostenitore.email_contatto = email_fittizzia()
        sostenitore.codice_fiscale = codice_fiscale()
        sostenitore.save()
        Appartenenza.objects.create(
            persona=sostenitore,
            sede=sede,
            membro=Appartenenza.SOSTENITORE,
            inizio="1980-12-10",
        )

        aspirante1 = crea_persona()
        aspirante1.email_contatto = email_fittizzia()
        aspirante1.codice_fiscale = codice_fiscale()
        aspirante1.save()
        a = Aspirante(persona=aspirante1)
        a.locazione = sede.locazione
        a.save()
        crea_utenza(aspirante1, aspirante1.email_contatto)

        aspirante2 = crea_persona()
        aspirante2.email_contatto = email_fittizzia()
        aspirante2.codice_fiscale = codice_fiscale()
        aspirante2.save()
        a = Aspirante(persona=aspirante2)
        a.locazione = sede.locazione
        a.save()
        crea_utenza(aspirante2, aspirante2.email_contatto)

        # Attività degli aspiranti
        sessione_aspirante1 = self.sessione_utente(persona=aspirante1)
        sessione_aspirante2 = self.sessione_utente(persona=aspirante2)
        sessione_aspirante1.click_link_by_partial_text("Richieste")
        self.assertTrue(sessione_aspirante1.is_text_present("Non ci sono richieste in attesa."), msg="Nessun invito")

        # setup dei dati
        oggi = poco_fa()
        corso = CorsoBase.objects.create(
            stato=CorsoBase.ATTIVO,
            sede=sede,
            data_inizio=oggi + timedelta(days=7),
            data_esame=oggi + timedelta(days=14),
            progressivo=1,
            anno=oggi.year,
            descrizione='Un corso',
        )
        self.client.login(username=presidente.email_contatto, password='prova')
        iscritti = {
            'persone': [aspirante1.pk]
        }
        self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritti)
        iscritti = {
            'persone': [aspirante2.pk]
        }
        self.client.post('/aspirante/corso-base/{}/iscritti/aggiungi/'.format(corso.pk), data=iscritti)
        self.assertEqual(corso.inviti.count(), 2)

        sessione_aspirante1.click_link_by_partial_text("Richieste")
        self.assertTrue(sessione_aspirante1.is_text_present(corso.nome), msg="Invito disponibile")
        sessione_aspirante1.click_link_by_partial_text("Conferma")
        self.assertTrue(sessione_aspirante1.is_text_present("Richiesta autorizzata."), msg="Richiesta autorizzata")

        self.assertEqual(corso.inviti.count(), 1)
        self.assertEqual(corso.partecipazioni.count(), 1)
        self.assertEqual(aspirante2.inviti_corsi.count(), 1)
        sessione_aspirante2.click_link_by_partial_text("Richieste")
        self.assertTrue(sessione_aspirante2.is_text_present(corso.nome), msg="Invito disponibile")
        sessione_aspirante2.click_link_by_partial_text("Nega")
        sessione_aspirante2.fill('motivo', 'Test')
        sessione_aspirante2.find_by_css(".btn-danger").first.click()
        self.assertTrue(sessione_aspirante2.is_text_present("Richiesta negata."), msg="Richiesta negata")
        self.assertEqual(corso.inviti.count(), 0)
        self.assertEqual(corso.partecipazioni.count(), 1)
        self.assertEqual(aspirante2.inviti_corsi.count(), 0)

    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per ricercare la posizione aspirante.")
    def test_registrazione_aspirante(self):
        """
        Effettua la registrazione come aspirante, il presidente
        del Comitato organizza un corso, avvisa tutti, l'aspirante trova
        un corso e vi ci si iscrive.
        """

        presidente = crea_persona()
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sessione_iniziale = self.sessione_anonimo()

        sessione_iniziale.click_link_by_partial_text("Iscriviti al prossimo corso base")

        sessione_iniziale.fill('codice_fiscale', 'MRARSS42A01C351F')
        sessione_iniziale.find_by_xpath('//button[@type="submit"]').first.click()

        email = email_fittizzia()
        sessione_iniziale.fill('email', email)
        sessione_iniziale.fill('password', 'ciao12345')
        sessione_iniziale.fill('ripeti_password', 'ciao12345')
        sessione_iniziale.find_by_xpath('//button[@type="submit"]').first.click()

        self.assertTrue(sessione_iniziale.is_text_present('è necessario cliccare sul link'),
                        msg="Invio email attivazione")
        self.sessione_termina(sessione_iniziale)

        # Estrazione della chiave di conferma
        self.assertTrue(len(mail.outbox), 1)
        body = mail.outbox[0].alternatives[0][0]
        url_conferma = re.findall('/registrati/aspirante/anagrafica/\?code=\w+&registration=\w+', body)[0]
        sessione_aspirante = self.sessione_anonimo()
        sessione_aspirante.visit("%s%s" % (self.live_server_url, url_conferma))

        sessione_aspirante.fill('nome', 'Mario')
        sessione_aspirante.fill('cognome', 'Rossi Accènto')
        sessione_aspirante.fill('data_nascita', '1/1/1942')
        sessione_aspirante.fill('comune_nascita', 'Catania')
        sessione_aspirante.fill('provincia_nascita', 'CT')
        sessione_aspirante.fill('indirizzo_residenza', 'Via Etnea 353')
        sessione_aspirante.fill('comune_residenza', 'Catania')
        sessione_aspirante.fill('provincia_residenza', 'CT')
        sessione_aspirante.fill('cap_residenza', '95128')
        sessione_aspirante.find_by_xpath('//button[@type="submit"]').first.click()

        self.assertTrue(sessione_aspirante.is_text_present("acconsenti al trattamento "
                                                           "dei tuoi dati personali"),
                        msg="Presente clausola di accettazione trattamento dei dati personali")

        sessione_aspirante.find_by_xpath('//button[@type="submit"]').first.click()

        self.assertTrue(sessione_aspirante.is_text_present("Ciao, Mario"),
                        msg="Login effettuato automaticamente")

        self.assertTrue(sessione_aspirante.is_text_present(email),
                        msg="Indirizzo e-mail visibile e mostrato correttamente")

        sede.locazione = Locazione.objects.filter(comune="Catania").first()
        sede.save()

        sessione_presidente = self.sessione_utente(persona=presidente)
        sessione_presidente.click_link_by_partial_text("Formazione")
        sessione_presidente.click_link_by_partial_text("Domanda formativa")

        self.assertTrue(sessione_presidente.is_text_present("1 aspiranti"),
                        msg="Aspirante correttamente considerato in domanda formativa")

        sessione_presidente.click_link_by_partial_text("Elenco Corsi Base")
        sessione_presidente.click_link_by_partial_text("Pianifica nuovo")

        sessione_presidente.select('sede', sede.pk)
        sessione_presidente.find_by_xpath('//button[@type="submit"]').first.click()
        self.sessione_conferma(sessione_presidente, accetta=True)

        self.seleziona_delegato(sessione_presidente, direttore)

        self.assertTrue(sessione_presidente.is_text_present("Corso Base pianificato"),
                        msg="Conferma che il corso base e' stato creato")

        self.assertTrue(sessione_presidente.is_text_present(direttore.nome_completo),
                        msg="Il nome completo del direttore viene mostrato")

        self.sessione_termina(sessione_presidente)  # Non abbiamo piu' bisogno del presidente

        sessione_direttore = self.sessione_utente(persona=direttore)
        sessione_direttore.click_link_by_partial_text("Formazione")
        sessione_direttore.click_link_by_partial_text("Elenco Corsi Base")

        self.assertTrue(sessione_direttore.is_text_present("Corso Base"),
                        msg="Corso base in lista")

        self.assertTrue(sessione_direttore.is_text_present("In preparazione"),
                        msg="Il corso appare con lo stato corretto")

        sessione_direttore.click_link_by_partial_text("Corso Base")

        self.assertTrue(sessione_direttore.is_text_present("Non c'è tempo da perdere"),
                        msg="Visibile promemoria corso che sta per iniziare a breve")

        self.assertTrue(sessione_direttore.is_text_present("1 aspiranti"),
                        msg="Visibile numero di aspiranti nelle vicinanze")

        sessione_direttore.click_link_by_partial_text("Gestione corso")
        self.scrivi_tinymce(sessione_direttore, "descrizione", "Sarà un corso bellissimo")
        sessione_direttore.find_by_xpath('//button[@type="submit"]').first.click()

        sessione_direttore.click_link_by_partial_text("Attiva il corso e informa gli aspiranti")

        self.assertTrue(sessione_direttore.is_text_present("Anteprima messaggio"),
                        msg="Anteprima del messaggio visibile")

        self.assertTrue(sessione_direttore.is_text_present("Sarà un corso bellissimo"),
                        msg="La descrizione del corso e' nell'anteprima del messaggio")
        sessione_direttore.find_by_xpath('//button[@type="submit"]').first.click()

        self.sessione_conferma(sessione_direttore, accetta=True)

        self.assertTrue(sessione_direttore.is_text_present("Corso attivato con successo"),
                        msg="Messaggio di conferma attivazione corso")

        if os.environ.get('TRAVIS', 'false') == 'true':
            self.skipTest('Questo test fallisce su travis senza motivo apparente')
        sessione_aspirante.click_link_by_partial_text("Posta")
        self.assertTrue(sessione_aspirante.is_text_present("Nuovo Corso per Volontari CRI"),
                        msg="E-mail di attivazione corso ricevuta")
        sessione_aspirante.click_link_by_partial_text("Nuovo Corso per Volontari CRI")
        self.assertTrue(sessione_aspirante.is_text_present("Sarà un corso bellissimo"),
                        msg="La descrizione del corso è stata comunicata per e-mail")
        sessione_aspirante.visit("%s/utente/" % self.live_server_url)

        sessione_aspirante.click_link_by_partial_text("Aspirante")
        sessione_aspirante.click_link_by_partial_text("Elenco dei corsi nelle vicinanze")

        self.assertTrue(sessione_aspirante.is_text_present(direttore.nome_completo),
                        msg="Il nome completo del Direttore e' visibile in elenco")

        sessione_aspirante.click_link_by_partial_text("Corso Base")
        sessione_aspirante.click_link_by_partial_text("Voglio iscrivermi a questo corso")

        self.assertTrue(sessione_aspirante.is_text_present("Abbiamo inoltrato la tua richiesta"),
                        msg="Conferma data all'aspirante")

        sessione_direttore.visit("%s/utente/" % self.live_server_url)
        sessione_direttore.click_link_by_partial_text("Richieste")
        self.assertTrue(sessione_direttore.is_text_present("chiede di essere contattato"),
                        msg="Esplicitare che l'aspirante vuole essere contattato")

        sessione_direttore.click_link_by_partial_text("Conferma")
        sessione_direttore.check('conferma_1')
        sessione_direttore.check('conferma_2')
        sessione_direttore.find_by_xpath('//button[@type="submit"]').first.click()

        sessione_aspirante.visit("%s/utente/" % self.live_server_url)
        sessione_aspirante.click_link_by_partial_text("Aspirante")
        self.assertTrue(sessione_aspirante.is_text_present("Sei iscritt"),
                        msg="Conferma di iscrizione")

        sessione_aspirante.click_link_by_partial_text("Vai alla pagina del Corso Base")
        self.assertTrue(sessione_aspirante.is_text_present("Presentati alle lezioni del corso"),
                        msg="Invita l'aspirante a presentarsi alle lezioni del corso")
