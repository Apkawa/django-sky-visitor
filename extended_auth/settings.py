# Copyright 2012 Concentric Sky, Inc.
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

"""
Default settings. See __init__.py for code that injects these defaults
"""

# Defaults to auth.User in case you don't want to take advantage of user subclassing features of this app
EXTENDED_AUTH_USER_MODEL = 'django.contrib.auth.User'

# This must be set to the python path (not including .models) of your primary subclass of User.
# Also, extended_auth.models.User will always contain this class as a shortcut
#EXTENDED_AUTH_USER_MODEL = None

# This setting is used only if your user model inherits from ExtendedUser rather than EmailExtendedUser. If you use ExtendedUser directly,
# and this settings is true, then the default forms will show email forms intead of login forms.
# TODO: Implement this
#EXTENDED_AUTH_EMAIL_LOGIN = False


app_default_settings = vars()

def get_app_setting(s, d=None):
    """
    Returns the first instance of the setting `s` that can be found in the order of priority: end user setting, the default `d` passed into the function, the app default setting specified in this file
    """
    import sys
    from django.conf import settings
    global app_default_settings
    try:
        app_default = app_default_settings[s]
    except KeyError:
        pass
    return getattr(settings, s, d or app_default)
