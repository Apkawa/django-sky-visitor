from django.conf import settings
from django.utils.unittest import skipUnless


def skipUnlessCustomUser(test_func):
    """
    Skip a test if a custom user model is in use.
    """
    return skipUnless(settings.AUTH_USER_MODEL != 'auth.User', 'Custom user model in use')(test_func)
