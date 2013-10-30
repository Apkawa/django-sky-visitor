# -*- coding: utf-8 -*-
from forms import InvitationStartForm


def create_invitation(email, name):
    form = InvitationStartForm(data={'email': email, 'name': name})
    if form.is_valid():
        return form.save()
    return None

