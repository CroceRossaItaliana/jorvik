from autenticazione.utils_test import TestFunzionale
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, email_fittizzia
from base.geo import Locazione
from jorvik.settings import GOOGLE_KEY
from unittest import skipIf


class TestFunzionaleFormazione(TestFunzionale):
    """
    Questa classe raccoglie i test funzionali per la formazione
    in Gaia.
    """

    @skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per ricercare la posizione aspirante.")
    def test_registrazione_aspirante(self):
        """
        Effettua la registrazione come aspirante, il presidente
        del Comitato organizza un corso, avvisa tutti, l'aspirante trova
        un corso e vi ci si iscrive.
        """

        presidente = crea_persona()
        direttore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sessione_aspirante = self.sessione_anonimo()

        sessione_aspirante.click_link_by_partial_text("Iscriviti al prossimo corso base")

        sessione_aspirante.fill('codice_fiscale', 'MRARSS42A01C351F')
        sessione_aspirante.find_by_xpath('//button[@type="submit"]').first.click()

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

        email = email_fittizzia()
        sessione_aspirante.fill('email', email)
        sessione_aspirante.fill('password', 'ciao12345')
        sessione_aspirante.fill('ripeti_password', 'ciao12345')
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
