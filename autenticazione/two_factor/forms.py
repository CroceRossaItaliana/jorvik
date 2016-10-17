# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from two_factor.forms import AuthenticationTokenForm


class JorvikAuthenticationTokenForm(AuthenticationTokenForm):

    def __init__(self, *args, **kwargs):
        if kwargs['user'].staticdevice_set.filter(name='backup').exists():
            self.base_fields['otp_token'].widget.is_required  = False
        super(JorvikAuthenticationTokenForm, self).__init__(*args, **kwargs)
