# -*- coding: utf-8 -*-
from django.template import Template, Context, loader, TemplateDoesNotExist
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import striptags


class BaseTemplateSender(object):
    def send(self, template_name, to_address, text_template_name=None,
             subject='', context=None, from_email=None, **kwargs):
        pass


class DjangoTemplateSender(BaseTemplateSender):
    def render(self, template_name, context):
        t = loader.get_template(template_name)
        return t.render(Context(context))

    def _render_from_string(self, s, context):
        t = Template(s)
        return t.render(Context(context))

    def send(self, template_name, to_address, text_template_name=None,
             subject='', context=None, from_email=None, **kwargs):
        context = context or {}
        html_body = self.render(template_name, context)
        try:
            text_body = self.render(text_template_name, context)
        except TemplateDoesNotExist:
            text_body = striptags(html_body)

        subject = self._render_from_string(subject, context)
        if isinstance(to_address, (str, unicode)):
            to_address = (to_address,)

        msg = EmailMultiAlternatives(subject=subject, body=text_body,
            from_email=from_email, to=to_address)
        msg.attach_alternative(html_body, "text/html")
        return msg.send()





