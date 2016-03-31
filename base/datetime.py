from bootstrap3.renderers import FieldRenderer
from bootstrap3.utils import add_css_class
from django.forms.widgets import DateTimeInput, DateInput


class DateTimeFieldRenderer(FieldRenderer):
    """
    Questa e' la classe renderer personalizzata che estende
    la classe del modulo bootstrap3 e si occupa di aggiungere
    classi CSS personalizzate ad alcuni tipi di campi.
    """

    def add_class_attrs(self, widget=None):
        super(DateTimeFieldRenderer, self).add_class_attrs(widget=widget)
        classes = widget.attrs.get('class', '')

        if isinstance(widget, DateTimeInput):  # Ora e data
            classes = add_css_class(classes, 'selettore-data-ora')

        elif isinstance(widget, DateInput):  # Solo data
            classes = add_css_class(classes, 'selettore-data')

        widget.attrs['class'] = classes
