import hashlib
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from django.utils.crypto import constant_time_compare
from django.utils.datastructures import SortedDict

__author__ = 'alfioemanuele'

"""
Contiene la funzione di hasing per la retrocompatibilita' con il Progetto Gaia originario.
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
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('iterations'), iterations),
            (_('salt'), mask_hash(salt)),
            (_('hash'), mask_hash(hash)),
        ])

    def must_update(self, encoded):
        return True
