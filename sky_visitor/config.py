# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.module_loading import import_string


TEMPLATE_EMAIL_SENDER = getattr(settings, 'SKY_TEMPLATE_EMAIL_SENDER', 'sky_visitor.template_email_senders.DjangoTemplateSender')
TEMPLATE_EMAIL_SENDER_CLASS = import_string(TEMPLATE_EMAIL_SENDER)

SEND_USER_PASSWORD = getattr(settings, 'SKY_SEND_USER_PASSWORD', False)
