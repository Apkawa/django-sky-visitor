A full featured authentication and user system that extends the default Django contib.auth pacakge.

**Note:** Version 0.8.1. This library is under active development. While in active development, the API will be changing frequently.


# Features

  * Class-based view implementations of all of the views
  * Email-based authentication. Entirely hides username from the user experience and allows an email-focused experience.
  * Invitations
  * Password rules
  * Subclass the User model to add your own fields, making queries easier to write (this will be deprecated when Django core implements their solution)

This library addresses many of the problems discussed on the Django wiki about [how to improve contrib.auth](https://code.djangoproject.com/wiki/ContribAuthImprovements).

## Subclassing User
The Django core developers are working on creating a solution for adding fields to the user model (see [discussion thread](https://groups.google.com/forum/#!topic/django-developers/PLTW8Mon9QU/discussion)). Please be advised that when Django core adds support for extending user fields, this app will depricate it's subclassing solution and provide an upgrade path.


# Usage
Throughout this app, any class beginning with `Email` indicates that it is for use with email-only authentication systems.
In all cases, there should be a matching class without `Email` at the beginning of the class name that is for use with username-focused authentication systems.

## Quickstart

  * `pip install git+ssh://git@github.com/concentricsky/django-sky-visitor.git`
  * Add `sky_visitor` near the top of your `INSTALLED_APPS` setting
  * Somewhere in your own `myapp.models.py`, define one of the two following code blocks:

```python
# Assume this is in myapp.models
from sky_visitor import EmailExtendedUser, EmailUserManager

class User(EmailExtendedUser):
    objects = EmailUserManager()
```

  * In your're `settings.py` add these lines:

```python

# Add this line to your INSTALLED_APPS
INSTALLED_APPS = [
    'sky_visitor',
    # ...
]

# Specify a URL to redirect to after login
LOGIN_REDIRECT_URL = '/'
```

## Sublcassing User model

Add the following to your settings.py if you wish to subclass the User model:

```python
# Change myapp to the name of the app where you extend EmailExtendedUser
SKY_VISITOR_USER_MODEL = 'myapp.User'
AUTHENTICATION_BACKENDS = [
    'sky_visitor.backends.EmailBackend',
]
```


## Advanced usage

  * Override URLs and views to provide custom workflows
  * Customize views and URLs
  * Customize forms
  * Choose to not automatically log a user in after they compelte a registration, or password reset
  * Don't create users with `manage.py createsuperuser` or `django.contrib.auth.models.User.create_user()` because there won't be a proper entry in the subclassed user table for them
  * On EmailExtendedUser you can set `validate_email_uniqeness` to false if you're concerned about the extra database query for each call to clean()

### Messages
This app uses the [messages framework](https://docs.djangoproject.com/en/dev/ref/contrib/messages/) to pass success messages
around after certain events (password reset completion, for example). If you would like to improve the experience for
your users in this way, make sure you follow the message framework docs to enable and render these messages on your site.


# Settings
Must specify `SECRET_KEY` in your settings for any emails with tokens to be secure (example: invitation, confirm email address, forgot password, etc)


# Admin
By default, we remove the admin screens for `auth.User` and place in an admin screen for SKY_VISITOR_USER_MODEL.

If you want to re-add the the django contrib user, you can do that by re-registering django.contrib.auth.User

If you want fine-grained control over the admin you can subclass the sky_visitor `UserAdmin`. Commonly, you will want to do this if you have subclassed ExtendedUser or EmailExtendedUser and you want your custom fields available in the admin. You can add fields in __init__, or just redefine the fieldsets and/or add_fieldsets attributes:

```python
from sky_visitor.admin import UserAdmin

class MyUserAdmin(UserAdmin):

    #completely redefine fieldsets for the add form
    add_fieldsets = (
        (None, {'fields': ('email', 'oauth_provider'), 'classes': ('skinny',)}),
    )

    #update the change form fieldsets
    def __init__(self, *args, **kwargs):
        super(UserAdmin, self).__init__(*args, **kwargs)

        #add a field to an existing fieldset
        for name, data in self.fieldsets:
            fields = data['fields']
            if 'password' in fields:
                fields_copy = [f for f in fields]
                fields_copy.append('password_hint')
                data['fields'] = tuple(fields_copy)

        #add a new fieldset
        fieldset_copy = [f for f in self.fieldsets]
        to_add = (_('Favorites'), {'fields': ('color', 'book', 'album')})
        fieldset_copy.append(to_add)
        self.fieldsets = tuple(fieldset_copy)

   # ...

admin.site.unregister(MyUser)
admin.site.register(MyUser, MyUserAdmin)
```
Note: Be sure to re-register your model with your new admin class.


# Testing

Tests are broken into three separate apps running under three different "modes":

  1. "auth user" mode (default)
    * Uses `example_project/settings.py`
    * Uses `django.contrib.auth.models.User` as the user model
    * Contains most of the tests
  2. "email user" mode
    * Uses `email_tests/settings.py`
    * Uses `email_tests.models.User` (a subclass of `sky_visitor.models.EmailExtendedUser`) as the user model
  2. "username user" mode
    * Uses `username_tests/settings.py`
    * Uses `username_tests.models.User` (a subclass of `sky_visitor.models.ExtendedUser`) as the user model


A test runner is configured in each settings.py to run only the tests that are appropriate.

You can run the tests like so:

    cd example_project
    # "auth user" tests
    ./manage.py test
    # "email user" tests
    ./manage.py test --settings=email_tests.settings
    # Run username-based tests
    ./manage.py test --settings=username_tests.settings


# Roadmap

Development TODO list:

  * Invitation clean up and tests
  * Fix setup.py

Features to add:

  * Admin login form should handle email-only authentication
  * Email confirmation on registration
  * Implement `LOGOUT_REDIRECT_URL`
  * Better built in password rules. Options for extending the password rules.
  * Refactor token URL generation to `utils.py`
  * Change email form and email confirmation page
  * Ability to add, link, and confirm multiple email addresses to the same account (separate app)

Improvements to documentation:

  * Write sphinx documentation
  * Step by step of password reset process and how it works
  * List all template paths that the default templates will look for
  * Add link to blog post about subclassing the user


# Contributing
Please fork this repo and send pull requests. Submit issues/questions/suggestions in the [issue queue](https://github.com/concentricsky/django-sky-visitor/issues).


# Author
Built at [Concentric Sky](http://www.concentricsky.com/) by [Jeremy Blanchard](http://github.com/auzigog/).

This project is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). Copyright 2012 Concentric Sky, Inc.


[discussion]:

