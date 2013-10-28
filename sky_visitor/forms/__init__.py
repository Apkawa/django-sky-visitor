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

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import forms as auth_forms, get_user_model

from sky_visitor.forms.fields import PasswordRulesField
from sky_visitor.models import InvitedUser
from ..config import SEND_USER_PASSWORD


class RegisterForm(auth_forms.UserCreationForm):

    class Meta:
        UserModel = get_user_model()

        model = UserModel
        fields = [UserModel.USERNAME_FIELD] + UserModel.REQUIRED_FIELDS

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        UserModel = get_user_model()
        if UserModel.USERNAME_FIELD != 'username':
            del self.fields['username']

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        UserModel = self.Meta.model
        username = self.cleaned_data["username"]
        try:
            UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class LoginForm(auth_forms.AuthenticationForm):
    # Note: The username field will always be called 'username' despite what UserModel.USERNAME_FIELD is
    pass


class PasswordResetForm(auth_forms.PasswordResetForm):

    def save(self, *args, **kwargs):
        """
        Override standard forgot password email sending. Sending now occurs in the view.
        """
        return


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = PasswordRulesField(label=_("New password"))


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    new_password1 = PasswordRulesField(label=_("New password"))


class InvitationStartForm(forms.ModelForm):

    class Meta:
        model = InvitedUser
        fields = ['email', 'name']

    def __init__(self, *args, **kwargs):
        super(InvitationStartForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        UserModel = get_user_model()
        if UserModel._default_manager.filter(username=username).exists():
            raise ValidationError(_("User with this username already exists."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # We need to verify that the user being invited doesn't already exist in the normal user table. Unique check is already done automatically for the InvitedUser table.
        UserModel = get_user_model()
        if UserModel._default_manager.filter(email=email).exists():
            raise ValidationError(_("User with this email already exists."))
        return email

    def save(self, commit=True):
        user = super(InvitationStartForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class InvitationCompleteForm(RegisterForm):

    def __init__(self, invited_user, *args, **kwargs):
        self.invited_user = invited_user
        initial = kwargs.get('initial', None)
        if 'email' not in initial:
            initial.update({'email': self.invited_user.email})

        super(InvitationCompleteForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        If commit=False, then call `form.save_invited_user() to finish saving the invited_user once the new (normal) user has a pk.
        """
        user = super(InvitationCompleteForm, self).save(commit)

        def save_invited_user():
            invited_user = self.invited_user
            invited_user.created_user = user
            invited_user.status = InvitedUser.STATUS_REGISTERED
            invited_user.save()

        if commit:
            save_invited_user()
        else:
            self.save_invited_user = save_invited_user
        return user
