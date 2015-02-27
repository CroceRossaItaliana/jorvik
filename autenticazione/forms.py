from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from anagrafica.models import Persona

class ModuloCreazioneUtenza(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(ModuloCreazioneUtenza, self).__init__(*args, **kargs)
        del self.fields['username']

    model = Persona
    fields = ("email")


class ModuloModificaUtenza(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(ModuloModificaUtenza, self).__init__(*args, **kargs)
        del self.fields['username']

    model = Persona
