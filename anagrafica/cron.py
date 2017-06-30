from datetime import datetime, timedelta

from django_cron import CronJobBase, Schedule

from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from anagrafica.models import Sede
from anagrafica.utils import termina_deleghe_giovani
from base.files import Excel, FoglioExcel
from base.utils import poco_fa
from jorvik.settings import DESTINATARI_REPORT
from posta.models import Messaggio


class CronReportComitati(CronJobBase):

    RUN_AT_TIMES = ['06:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'anagrafica.report.sedi'

    def do(self):

        sedi = Sede.objects.filter(
            attiva=True, tipo=Sede.COMITATO,
            estensione__in=[NAZIONALE, REGIONALE,
                            PROVINCIALE, LOCALE]
        ).prefetch_related("locazione").order_by('nome')

        excel = Excel(oggetto=sedi.first())
        foglio = FoglioExcel("Report", [
            "Denominazione", "Tipo", "Regione", "Provincia",
            "Via", "Città", "CAP", "Telefono", "FAX",
            "Email", "Sito web", "Denominazione",
            "Referente", "Codice Fiscale", "Partita IVA",
            "IBAN", "PEC", "Ultima modifica",
            "Extra: Titolo", "Extra: Testo"
        ])

        for sede in sedi:

            # Denominazione: Rimuovi termini di troppo
            denominazione = sede.nome.replace(" Provinciale", "")
            estensione = {
                NAZIONALE: "CN",
                REGIONALE: "CR",
                PROVINCIALE: "CP",
                LOCALE: "CL"
            }[sede.estensione]
            regione = sede.locazione.regione if sede.locazione else ""
            provincia = sede.locazione.provincia_breve if sede.locazione else ""
            via = "%s, %s" % (sede.locazione.via, sede.locazione.civico) if sede.locazione else ""
            citta = sede.locazione.comune if sede.locazione else ""
            cap = sede.locazione.cap if sede.locazione else ""
            presidente = sede.presidente() or ""

            extra_titolo = ""
            extra_testo = ""

            unita = sede.ottieni_figli().filter(estensione=TERRITORIALE)
            if unita.exists():
                extra_titolo = "<h2>Le nostre unità territoriali</h2>"
                extra_testo += "<ul>"
                for u in unita:
                    extra_testo += "<li>Sede CRI di %s%s</li>" % (
                        u.nome,
                        (" &mdash; e-mail: %s" % u.email) if u.email else ""
                    )
                extra_testo += "</ul>"

            foglio.aggiungi_riga(
                denominazione,
                estensione,
                regione,
                provincia,
                via,
                citta,
                cap,
                sede.telefono,
                sede.fax,
                sede.email,
                sede.sito_web,
                "Presidente/Commissario CRI",
                presidente,
                sede.codice_fiscale,
                sede.partita_iva,
                sede.iban,
                sede.pec,
                sede.ultima_modifica,
                extra_titolo,
                extra_testo,
            )

        excel.aggiungi_foglio(foglio)

        tra_una_settimana = poco_fa() + timedelta(days=7)
        excel.genera_e_salva(nome="Report.xlsx", scadenza=tra_una_settimana)

        data = datetime.today().strftime("%d/%m/%Y")

        Messaggio.invia_raw(
            oggetto="(SVI) Report Sedi CRI - %s" % data,
            corpo_html="In allegato è presente il report excel delle Sedi CRI, "
                       "aggiornato al %s." % data,
            email_mittente="%s <%s>" % (Messaggio.SUPPORTO_NOME, Messaggio.NOREPLY_EMAIL),
            lista_email_destinatari=DESTINATARI_REPORT,
            allegati=[excel]
        )

        print("Inviato report sedi ai seguenti indirizzi: %s" % ", ".join(DESTINATARI_REPORT))


def CronTerminaNonGiovani(CronJobBase):

    RUN_AT_TIMES = ['06:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'anagrafica.termina_deleghe_giovani'

    def do(self):
        termina_deleghe_giovani()
