Installation
============

.. warning:: This documentation is not final. Do not rely on the information here.

.. important:: This installation assumes a Debian based OS

Requirements
------------

::

    python3.6+
    qbittorrent or qbittorrent-nox
    ffmpeg
    git
    npm
    yarn
    make
    Clang v3.4+
    GCC v5.1+

Installing qbittorrent-nox
--------------------------

This projects uses `python-qbittorrent <https://pypi.org/project/python-qbittorrent/>`_ and this package requires qbittorrent 4.1+

If your distro does not contain 4.1+, you can add them via the following:


``sudo add-apt-repository ppa:qbittorrent-team/qbittorrent-stable``

``sudo apt update``

If you are running this on your server, you may want to run qbittorrent as headless.
`qbittorrent-nox` is a headless program that launches Web-UI which is how this service communicates with.
To install `qbittorrent-nox`, run

``sudo apt install -y qbittorrent-nox``

In order to run `qbittorrent-nox` every time the machine starts, you can create systemd service.
In order to do this, create `qbittorrent-nox.service` file under `/etc/systemd/system/`


.. code-block:: bash

   """ /etc/systemd/system/qbittorrent-nox.service """

   Description=qBittorrent Command Line Client
   After=network.target

   [Service]
   # Do not change to "simple"
   Type=forking
   User=qbittorrent-nox
   Group=qbittorrent-nox
   UMask=007
   ExecStart=/usr/bin/qbittorrent-nox -d --webui-port=9000
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target


Setting up systemd for celery
-----------------------------

.. code-block:: bash

    """ /etc/systemd/system/celery-vigilio.service """

    [Unit]
    Description=Celery workers
    After=network.target redis.target

    [Service]
    Type=forking
    User=user
    Group=user
    EnvironmentFile=-/home/user/vigilio/celery.conf
    WorkingDirectory=/home/user/vigilio/
    PermissionsStartOnly=true
    ExecStart=/home/user/vigilio/venv/bin/celery multi start $CELERYD_NODES \
        -A $CELERY_APP --pidfile=${CELERYD_PID_FILE} \
        --logfile=${CELERYD_LOG_FILE} --loglevel="${CELERYD_LOG_LEVEL}" \
        $CELERYD_OPTS
    ExecStop=/home/user/vigilio/venv/bin/celery multi stopwait $CELERYD_NODES \
        --pidfile=${CELERYD_PID_FILE}
    ExecReload=/home/user/vigilio/venv/bin/celery multi restart $CELERYD_NODES \
        -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
        --logfile=${CELERYD_LOG_FILE} --loglevel="${CELERYD_LOG_LEVEL}" \
        $CELERYD_OPTS

    [Install]
    WantedBy=multi-user.target


.. code-block::

    """ /home/user/vigilio/celery.conf """

    DJANGO_SETTINGS_MODULE="watch.settings.prod"
    CELERY_APP="watch:celery_app"

    # Worker settings
    CELERYD_NODES="w1"
    CELERYD_OPTS="--concurrency=3"
    CELERYD_LOG_FILE="/var/log/celery/celery-%N.log"
    CELERYD_PID_FILE="/var/log/celery/pid-%N.pid"
    CELERYD_LOG_LEVEL="INFO"
