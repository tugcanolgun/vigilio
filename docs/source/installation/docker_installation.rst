Docker Installation
===================

Docker is the easiest and fastest way to install Vigilio. In order to install Vigilio via
docker, you need to have both docker and docker-compose installed. You can find instructions
on how to install docker and docker-compose by following links.

| `docker <https://docs.docker.com/engine/install/>`_
| `docker-compose <https://docs.docker.com/compose/install/>`_

How to install and run Vigilio
------------------------------

| ``git clone https://github.com/tugcanolgun/vigilio.git``
| ``cd vigilio``
| ``docker-compose up -d``

| After docker-compose finished building and successfully run the server, you can reach it at
| ``http://localhost:8000``

| Default username: ``admin``
| Default password: ``adminadmin``

 .. important:: Please head to `After Installation <./after_installation.html>`_ page to see the instructions on how to set up Vigilio.

Change default port
-------------------

You can change the default port ``8000`` by changing the port value under ``nginx`` in ``docker-compose.yml`` file.


Running docker behind nginx
---------------------------

It is recommended that you run docker behind nginx. Assuming
