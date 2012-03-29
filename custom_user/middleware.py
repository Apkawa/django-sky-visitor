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

from django.template import RequestContext, loader
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from custom_user.exceptions import Http403

def render_to_403(*args, **kwargs):
    """
        Returns a HttpResponseForbidden whose content is filled with the result of calling
        django.template.loader.render_to_string() with the passed arguments.
    """
    if not isinstance(args,list):
        args = list()
        args.append('403.html')

    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)

    return response

class Http403Middleware(object):
    def process_exception(self,request,exception):
        if isinstance(exception,Http403):
            return render_to_403(context_instance=RequestContext(request))
