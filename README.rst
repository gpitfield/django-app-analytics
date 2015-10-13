=====
Django App Analytics
=====

Django App Analytics is a small app that provides an endpoint for
analytics collection (typically from a mobile device), as well as a task
that can be used for analytics collection from the server. It also provides
a few meta-functions to aggregate analytics.

It will be evolved to provide more detailed reports over time.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "analytics" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'analytics',
    )

2. Run `python manage.py migrate` to create the analytics models.

3. Configure settings::

    ANALYTICS_SETTINGS = {
        'TBD' = True,
    }