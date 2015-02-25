"""
Questo modulo definisce i modelli del modulo anagrafico di Gaia.

- Persona
- Telefono
- Documento
- Utente
- Appartenenza
- Comitato
- Delega
"""

from base.modelli import *
from base.tratti import *
import phonenumbers


class Persona(ModelloCancellabile, ConGeolocalizzazioneRaggio):
    """
    Rappresenta un record anagrafico in Gaia.
    """

    class Meta:
        verbose_name_plural = "Persone"

    def aggiungi_numero_telefono(self, numero, servizio=False, paese="IT"):
        """
        Aggiunge un numero di telefono per la persona.
        :param numero: Il numero di telefono.
        :param servizio: Vero se il numero e' di servizio. Default False.
        :param paese: Suggerimento per il paese. Default "IT".
        :return: True se l'inserimento funziona, False se il numero e' mal formattato.
        """
        try:
            n = phonenumbers.parse(numero, paese)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False
        f = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
        t = Telefono(persona=self, numero=f, servizio=servizio)
        t.save()
        return True


class Telefono(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un numero di telefono.
    NON USARE DIRETTAMENTE. Usare i metodi in Persona.
    """

    persona = models.ForeignKey(Persona, related_name="numeri_telefono")
    numero = models.CharField("Numero di telefono", max_length=16)
    servizio = models.BooleanField("Numero di servizio", default=False)

    class Meta:
        verbose_name = "Numero di telefono"
        verbose_name_plural = "Numeri di telefono"

    def _phonenumber(self):
        return phonenumbers.parse(self.numero)

    def __str__(self):
        """
        Ritorna il numero per la visualizzazione nel formato appropriato (Italiano o Internazionale)
        :return: Stringa che rappresenta il numero di telefono.
        """
        n = self._phonenumber()
        if n.country_code == 39:
            return self.nazionale()
        else:
            return self.internazionale()

    def nazionale(self):
        """
        Ritorna il numero formattato come numero nazionale.
        :return: Stringa che rappresenta il numero in formato nazionale.
        """
        return phonenumbers.format_number(self._phonenumber(), phonenumbers.PhoneNumberFormat.NATIONAL)

    def internazionale(self):
        """
        Ritorna il numero formattato come numero internazionale.
        :return: Stringa che rappresenta il numero in formato internazionale.
        """
        return phonenumbers.format_number(self._phonenumber(), phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    def e164(self):
        """
        Ritorna il numero formattato come numero internazionale E.164.
        :return: Stringa che rappresenta il numero in formato internazionale E.164.
        """
        return phonenumbers.format_number(self._phonenumber(), phonenumbers.PhoneNumberFormat.E164)




class Documento(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Documenti"


class Utenza(ModelloSemplice):

    class Meta:
        verbose_name_plural = "Utenze"


class Appartenenza(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):

    class Meta:
        verbose_name_plural = "Appartenenze"


class Comitato(ModelloAlbero, ConGeolocalizzazione):

    class Meta:
        verbose_name_plural = "Comitati"


class Delega(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Deleghe"
