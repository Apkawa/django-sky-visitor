from django import forms
from django.conf import settings
from django.contrib.auth import forms as auth_forms, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User as AuthUser
from custom_user.utils import SubclassedUser as User
from custom_user.fields import UniqueRequiredEmailField, PasswordRulesField


# All user forms should inherit from this form to make sure email is unique
class BaseUserCreateForm(forms.ModelForm):
    # TODO: Make email and non-email version
    email = UniqueRequiredEmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',]

    def __init__(self, *args, **kwargs):
        super(BaseUserCreateForm, self).__init__(*args, **kwargs)

        if 'first_name' in self.fields and 'last_name' in self.fields:
            self.fields['first_name'].required = True
            self.fields['last_name'].required = True

class UserCreateAdminForm(forms.ModelForm):
    # TODO: Make email and non-email version
    password1 = PasswordRulesField(label=_("Password"))
    username = None
    # TODO: Need a way to have a username-based option and an email-based option

    def __init__(self, *args, **kwargs):
        super(UserCreateAdminForm, self).__init__(*args, **kwargs)

    email = UniqueRequiredEmailField()
    password1 = PasswordRulesField(label=_("Password"))
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ['email',]
        exclude = ['username',]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def save(self, commit=True):
        user = super(UserCreateAdminForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeAdminForm(auth_forms.UserChangeForm):
    email = UniqueRequiredEmailField()
    # TODO: Need a way to have a username-based option and an email-based option


# TODO: Inheriting from this form creates a auth.User instead of a subclassed User. Fix that.
class RegisterForm(auth_forms.UserCreationForm):
    # TODO: Make email and non-email version
    email = UniqueRequiredEmailField()

    class Meta:
        model = User
        fields = ['username', 'email',]


class InvitationForm(BaseUserCreateForm):
    # TODO: Make email and non-email version
    email = UniqueRequiredEmailField()

    def save(self, commit=True):
        user = super(InvitationForm, self).save(commit=False)
        # Make them unactivated
        user.is_active = False
        if commit:
            user.save()
        return user


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = PasswordRulesField(label=_("New password"))


# Borrowed from core so we can define our own inheritance
class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']


class InvitationCompleteForm(forms.ModelForm):
    # TODO: Make email and non-email version
    email = UniqueRequiredEmailField()
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