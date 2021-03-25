Development
===========

Requirements
------------

::

    python3.6+
    python3-venv
    git
    redis-server
    yarn
    make

    # Optional
    ffmpeg
    qbittorrent or qbittorrent-nox


Backend Installation
--------------------

Redis
^^^^^

If your redis server is running on port different than ``6379``,
you can change it in ``.env`` file under ``CELERY_BROKER_URL`` and ``CELERY_RESULT_BACKEND``

You need to restart vigilio/celery when you change these settings.

Running vigilio
^^^^^^^^^^^^^^^

| If you are going to create a pull request and contribute to the project, fork the project and clone your project instead.
| ``git clone https://github.com/tugcanolgun/vigilio.git``

``cd vigilio``

``git checkout dev``

**Create your branch**

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Type
     - Example
   * - feature/your_feature
     - ``git checkout -b feature/your_feature``
   * - fix/your_fix
     - ``git checkout -b feature/your_fix``

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

You need to have ``yarn`` installed on your system. You can install the dependencies with:

``make install``

Development mode
^^^^^^^^^^^^^^^^

``make start``

Your changes should reflect on the page when you refresh the page you are working on.

Production mode
^^^^^^^^^^^^^^^

To run webpack in production mode and minimize bundles:

``make build``

