Development
===========

Requirements
------------

::

    python3.6+
    redis
    yarn
    make


Backend Installation
--------------------

Redis
^^^^^

If your redis server is running on port different than ``6379``,
you can change it in ``.env`` file under ``CELERY_BROKER_URL`` and ``CELERY_RESULT_BACKEND``

You need to restart vigilio/celery when you change these settings.

Getting and running repo
^^^^^^^^^^^^^^^^^^^^^^^^

``git clone https://github.com/tugcanolgun/vigilio.git``

``cd vigilio``

``python3.x -m venv venv && source venv/bin/activate``

``pip install -r requirements/dev.txt``

``./manage migrate``

``./manage runserver --settings=watch.settings.dev``

Running celery
^^^^^^^^^^^^^^

``source venv/bin/activate``

``celery -A watch worker -l INFO``

Frontend Installation
---------------------

``make install``

To run webpack in development mode:

``make start``

To run webpack in production mode and minimize bundles:

``make build``

