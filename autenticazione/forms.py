from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.forms import ModelForm
from anagrafica.models import Persona
from autenticazione.models import Utenza


class ModuloCreazioneUtenza(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    model = Utenza
    fields = ("email")


class ModuloModificaUtenza(ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField(
        help_text=_("Le password vengono salvate solamente in modo criptato, "
                    "quindi non c'e' modo di vedere la password di questo utente, "
                    "ma puoi cambiarla <a href=\"password/\">con questo modulo</a>.")
    )

    class Meta:
        model = Utenza
        fields = ('email', 'password', 'is_active', )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

