from django.forms import Textarea


class WYSIWYGSemplice(Textarea):
    def __init__(self, attrs=None):
        # Use slightly better defaults than HTML's 20x2 box
        default_attrs = {'class': 'wysiwyg-semplice'}
        if attrs:
            default_attrs.update(attrs)
        super(WYSIWYGSemplice, self).__init__(default_attrs)

