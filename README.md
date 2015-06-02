![Concentric Sky](https://concentricsky.com/media/uploads/images/csky_logo.jpg)


# Sky Visitor

Sky Visitor is an open-source Django library developed by [Concentric Sky](http://concentricsky.com/). It is a full-featured authentication and user system that complements django.contib.auth.

### Table of Contents
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [License](#license)
- [About Concentric Sky](#about-concentric-sky)


## Installation

Install this package using pip:

    pip install git+https://github.com/concentricsky/django-sky-visitor.git@v1.0.1

Add `'sky_visitor'` to your `INSTALLED_APPS` array.

    INSTALLED_APPS = [
        ...
        'sky_visitor',
        ...
    ]

You must specify `SECRET_KEY` in your settings for any emails with tokens to be secure (example: invitation, confirm email address, forgot password, etc)

You must at least set `LOGIN_URL` to `"login"`. You can optionally specify another valid URL or URL name of your own. Certain views in Sky Visitor depend on an accurate value for this setting and the default value in Django core (`"/authentication/login/"`) is likely invalid unless you have created it.


## Getting Started

If you wish to use the default URLs, add them to your `urls.py` like so:

    url(r'^user/', include('sky_visitor.urls')),

### Basic Features

  * Class-based view implementations of all of the views
  * Invitation emailed to users, where they can complete their registration
  * Password rules

### Advanced Usage

  * Override URLs and views to provide custom workflows
  * Customize views and URLs
  * Customize forms
  * Choose to not automatically log a user in after they compelte a registration, or password reset

### Messages

This app uses the [messages framework](https://docs.djangoproject.com/en/dev/ref/contrib/messages/) to pass success messages
around after certain events (password reset completion, for example). If you would like to improve the experience for
your users in this way, make sure you follow the message framework docs to enable and render these messages on your site.


## Testing

Tests are broken into two separate apps running under three different "modes":

  1. "normal user" mode (default)
    * Uses `normaluser_tests/settings.py`
    * Uses `django.contrib.auth.models.User` as the user model
    * Contains the base tests
  2. "custom user" mode
    * Uses `customuser_tests/settings.py`
    * Uses `django.contrib.auth.test.custom_user.CustomUser` as the user model

A test runner is configured in each settings.py to run only the tests that are appropriate.

You can run the tests like so:

    cd example_project
    # "normal user" tests
    ./manage.py test
    # "custom user" tests
    ./manage.py test --settings=customuser_tests.settings


## Roadmap

Features to add:

  * A user should have to confirm their email address before being allowed to finalize their registration
  * Implement `LOGOUT_REDIRECT_URL`
  * Better built in password rules. Options for extending the password rules.

Improvements to documentation:

  * Write sphinx documentation
  * Step by step of password reset process and how it works
  * List all template paths that the default templates will look for


## License

This project is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0). Details can be found in the LICENSE.md file.

### Contributing

Please fork this repo and send pull requests. Submit issues/questions/suggestions in the [issue queue](https://github.com/concentricsky/django-sky-visitor/issues).


## About Concentric Sky

_For nearly a decade, Concentric Sky has been building technology solutions that impact people everywhere. We work in the mobile, enterprise and web application spaces. Our team, based in Eugene Oregon, loves to solve complex problems. Concentric Sky believes in contributing back to our community and one of the ways we do that is by open sourcing our code on GitHub. Contact Concentric Sky at hello@concentricsky.com._
