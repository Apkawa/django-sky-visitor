# -*- coding: utf-8 -*-
import string
import random
import hashlib
import binascii
import cPickle as pickle
from Crypto.Cipher import AES

from django.conf import settings

class Encryption(object):

    def __init__(self, key=None):
        self.key = key or settings.SECRET_KEY

    def build_key(self, key):
        return hashlib.md5(key).hexdigest()

    def get_cipher_instance(self):
        key = self.build_key(self.key)
        return AES.new(key, AES.MODE_CBC, key[:16])

    def decrypt(self, enc_message):
        ciphertext = binascii.a2b_hex(enc_message)
        decryption_message = self.get_cipher_instance().decrypt(ciphertext).rstrip(' ')
        return pickle.loads(decryption_message)

    def encrypt(self, message):
        pickled = pickle.dumps(message)
        ciphertext = self.get_cipher_instance().encrypt(pickled + (' ' * (16 - (len(pickled) % 16))))
        enc_message = binascii.b2a_hex(ciphertext)
        return enc_message


def make_password(length=8, chars=string.ascii_letters):
    return ''.join(random.choice(chars) for _ in xrange(length))

