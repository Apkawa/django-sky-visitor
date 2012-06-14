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

from django import forms
from django.contrib.auth import forms as auth_forms, authenticate
from django.contrib.auth.models import User as AuthUser
from django.forms.fields import EmailField
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from sky_visitor.utils import SubclassedUser as User
from sky_visitor.forms.fields import PasswordRulesField


class NameRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(NameRequiredMixin, self).__init__(*args, **kwargs)
        if 'first_name' in self.fields and 'last_name' in self.fields:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

class UniqueEmailFormMixin(object):
    """
    When using this mixin, be sure to specify 'email' in your Form's Meta.fields.

    Support for adding this email field automatically to that list
    is unfinished, and commented out below.
    """
    nonunique_error = _("This email address is already in use. Please enter a different email address.")

    email = EmailField()

    # The following snippet adds the email field to the Form, but we still need to ensure this
    # works in all cases and does the whole job.  Not yet sure if we need to do anything special
    # for field label, whether this initial data is sufficient, etc.
    # Until we have some time to work through all the cases, just add 'email' to the
    # superclass's Meta.fields.
#    def __init__(self, *args, **kwargs):
#        super(UniqueEmailFormMixin, self).__init__(*args, **kwargs)
#        self.fields['email'] = self.email
#        if self.instance:
#            self.initial['email'] = self.instance.email

    def clean(self):
        email = self.cleaned_data.get('email')
        matching = AuthUser.objects.filter(email=email)
        if self.instance and self.instance.pk:
            matching = matching.exclude(pk=self.instance.pk)
        if matching:
            if 'email' not in self._errors:
                self._errors['email'] = ErrorList()
            self._errors['email'].append(self.nonunique_error)
        return super(UniqueEmailFormMixin, self).clean()


class RegisterBasicForm(auth_forms.UserCreationForm):
    """
    Use the default contrib.auth form here and change the model to our SubclassedUser
    """
    class Meta:
        model = User
        fields = ['username']


class RegisterForm(RegisterBasicForm):
    """
    Add email to the basic register form because the is a more common use case
    """
    class Meta:
        model = User
        fields = ['username', 'email']


class EmailRegisterForm(UniqueEmailFormMixin, forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = PasswordRulesField(label=_("Password"))
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ['email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(EmailRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserCreateAdminForm(auth_forms.UserCreationForm):
    password1 = PasswordRulesField(label=_("Password"))

    class Meta:
        model = User

class EmailUserCreateAdminForm(UserCreateAdminForm):
    def __init__(self, *args, **kwargs):
        super(EmailUserCreateAdminForm, self).__init__(*args, **kwargs)
        del self.fields['username']

class UserChangeAdminForm(auth_forms.UserChangeForm):
    class Meta:
        model = User

class EmailUserChangeAdminForm(UserChangeAdminForm):
    def __init__(self, *args, **kwargs):
        super(EmailUserChangeAdminForm, self).__init__(*args, **kwargs)
        del self.fields['username']

# TODO: Inheriting from this form creates a auth.User instead of a subclassed User. Fix that.
class RegisterForm(UniqueEmailFormMixin, auth_forms.UserCreationForm):
    # TODO: Make email and non-email version -- this is for email

    class Meta:
        model = User
        fields = ['username', 'email']


class InvitationForm(UniqueEmailFormMixin, forms.ModelForm):
    # TODO: Make email and non-email version -- this is for email

    class Meta:
        model = User
        fields = ['email']

    def save(self, commit=True):
        user = super(InvitationForm, self).save(commit=False)
        # Make them unactivated
        user.is_active = False
        if commit:
            user.save()
        return user


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = PasswordRulesField(label=_("New password"))


# Borrowed from django.contrib.auth so we can define our own inheritance
class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    })
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(self.error_messages['password_incorrect'])
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']


class InvitationCompleteForm(UniqueEmailFormMixin, forms.ModelForm):
    # TODO: Make email and non-email version -- this is for email

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class BaseLoginForm(forms.Form):
    # NOTE: We choose not to extend AuthenticationForm here because we only need username in one of the subclasses

    error_messages = {
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(BaseLoginForm, self).__init__(*args, **kwargs)

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class LoginForm(BaseLoginForm):
    username = forms.CharField(label=_("Username"), max_length=30)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.error_messages['invalid_login'] = _("Please enter a correct username and password. Note that both fields are case-sensitive.")
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        return self.cleaned_data


class EmailLoginForm(BaseLoginForm):
    email = forms.CharField(label=_("Email"), max_length=75)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.error_messages['invalid_login'] = _("Please enter a correct email and password. Note that both fields are case-sensitive.")
        super(EmailLoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        return self.cleaned_data


class PasswordResetForm(auth_forms.PasswordResetForm):
    def save(self, *args, **kwargs):
        """
        Override standard forgot password email sending. Sending now occurs in the view.
        """
        return


class ProfileEditForm(forms.ModelForm):
    # TODO: Make email and non-email version
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
