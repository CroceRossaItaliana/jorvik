import hashlib
from collections import OrderedDict

from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare

__author__ = 'alfioemanuele'

"""
Contiene la funzione di hashing per la retrocompatibilita' con il software originario del Progetto Gaia.

La password viene aggiornata al primo accesso. (must_update(...) => True).
"""

class RetroGaiaHasher(BasePasswordHasher):

    algorithm = "gaia"
    iterations = 1

    def salt(self):
        return ""

    def encode(self, password, salt):
        assert salt == ''
        password = str(password).encode('utf-8')
        hash = str(hashlib.md5(password).hexdigest())
        hash = str(hashlib.sha1(str(hash + "@CroceRossa").encode('utf-8')).hexdigest())
        return "%s$%d$%s$%s" % (self.algorithm, self.iterations, '', hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm

        encoded_2 = self.encode(password, '')
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        return OrderedDict([
            ('algorithm', algorithm),
            ('iterations', iterations),
            ('salt', mask_hash(salt)),
            ('hash', mask_hash(hash)),
        ])

    def must_update(self, encoded):
        return True
