# Copyright 2013 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime
from django.conf import settings
from django.db import models

from utils import Encryption, make_password


class InvitedUser(models.Model):
    STATUS_INVITED = 'invited'
    STATUS_REGISTERED = 'registered'
    STATUS_CHOICES = (
        (STATUS_INVITED, "Invited"),
        (STATUS_REGISTERED, "Registered"),
    )
    email = models.EmailField(max_length=254, unique=True)
    status = models.CharField(max_length=32, default=STATUS_INVITED, choices=STATUS_CHOICES)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    enc_password = models.CharField(max_length=256, null=True, blank=True)

    # We need to fake a few properties so we can use the default token generation code
    @property
    def last_login(self):
        if self.created_user and hasattr(self.created_user, 'last_login'):
            return self.created_user.last_login
        else:
            return datetime.datetime(2013, 1, 1, 0, 0, 0)

    @property
    def password(self):
        return ''

    def save(self, *args, **kwargs):
        if not self.enc_password:
            self.enc_password = self.encrypt_password(make_password())
        super(InvitedUser, self).save(*args, **kwargs)

    def get_encrypter(self):
        enc = Encryption(key="%s_%s" % (self.email, settings.SECRET_KEY))
        return enc

    def decrypt_password(self, enc_password=None):
        return self.get_encrypter().decrypt(enc_password or self.enc_password)

    def encrypt_password(self, password):
        return self.get_encrypter().encrypt(password)

