Manual Installation
===================

.. warning:: This process has not yet been tested on a completely new OS installation. There may be missing information.

.. important:: This installation assumes a Debian based OS

Requirements
------------

::

    python3.6+
    python3-venv
    qbittorrent or qbittorrent-nox
    ffmpeg
    git
    redis-server
    nginx
    make

Dependencies
------------

Installing python
^^^^^^^^^^^^^^^^^

Vigilio requires python3.6+

Even though not necessary, it is recommended to get the latest python version available.

You can search available python versions by running ``sudo apt search python3``. There are also non official
ppa sources such as `deadsnakes PPA <https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa>`_

Install python and python-venv via

``sudo apt install python3.x python3.x-venv``

Installing ffmpeg git make nginx redis-server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``sudo apt install ffmpeg git make nginx-full nginx-extras redis-server``

| ``systemctl start redis``
| ``systemctl enable redis``

Installing qbittorrent-nox
^^^^^^^^^^^^^^^^^^^^^^^^^^

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
   ExecStart=/usr/bin/qbittorrent-nox -d --webui-port=8080
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target


| ``systemctl start qbittorrent-nox.service``
| ``systemctl enable qbittorrent-nox.service``

Installing Vigilio
------------------

Get Vigilio with the following command,

``git clone https://github.com/tugcanolgun/vigilio.git``

Before going into the newly fetched folder, you will need to create some system files.

Setting up nginx
^^^^^^^^^^^^^^^^

Go to ``cd /etc/nginx`` and open ``nginx.conf`` with ``sudo nano nginx.conf`` or ``sudo vim nginx.conf``

Scroll down to ``#gzip on;`` and remove the ``#``. Below that add the following:

.. code-block:: bash

    """ /etc/nginx/nginx.conf """

    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

Save it by ``Ctrl+X`` and ``Y`` + `Enter`

Go to ``cd sites-enabled`` and open the file ``default`` or your domain file ``sudo nano default`` or
``sudo vim default``. The content of it should end up looking like the following. Replace
the paths and user.

.. code-block:: bash

    """ /etc/nginx/sites-enabled/default """

    ...
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/user/vigilio/watch.sock;
    }

    location /static/ {
        alias /home/user/vigilio/statics/;
    }

    location /downloads/ {
        mp4;
        mp4_buffer_size       1m;
        mp4_max_buffer_size   10m;
        alias /home/user/Downloads/;
    }

    location /media/ {
        alias /home/user/vigilio/media/;
    }
    ...


Setting up systemd for django
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a file with the following command ``sudo nano /etc/systemd/system/vigilio.service`` or
``sudo vim /etc/systemd/system/vigilio.service``

Paste the following and change the user and paths,

.. code-block:: bash

    """ /etc/systemd/system/vigilio.service """

    [Unit]
    Description=Vigilio gunicorn daemon
    After=network.target

    [Service]
    User=user
    Group=www-data
    WorkingDirectory=/home/user/vigilio
    ExecStart=/home/user/vigilio/venv/bin/gunicorn --preload --access-logfile - --workers 1 --bind unix:/home/user/vigilio/watch.sock watch.wsgi:application

    [Install]
    WantedBy=multi-user.target

``systemctl enable vigilio.service``

``sudo mkdir -p /var/log/celery && chown -R ${USER}:${USER} /var/log/celery``

Setting up systemd for celery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a file with the following command ``sudo nano /etc/systemd/system/celery-vigilio.service`` or
``sudo vim /etc/systemd/system/celery-vigilio.service``

Paste the following and change the user and paths,

.. code-block:: bash

    """ /etc/systemd/system/celery-vigilio.service """

    [Unit]
    Description=Celery workers for Vigilio
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


``systemctl enable celery-vigilio.service``

Running Vigilio
---------------

Finally, head over to ``vigilio`` folder that you downloaded ``cd ~/vigilio`` and run the following command

``make deploy``

If everything goes well, towards the end, you will be asked to enter your password twice to start (restart)
the systemd files that we just created.

After this you need to create a user with the following command ``venv/bin/python manage.py createsuperuser``

.. code-block:: bash

    Username:
    Email address:
    Password:
    Password (again):

    Superuser created successfully.

And that's it. Installation should be complete.

Anytime there is a new update, all you need to do is to run ``make deploy``. You won't need to touch anything
else anymore.


 .. important:: Please head to `After Installation <./after_installation.html>`_ page to see the instructions on how to set up Vigilio.

