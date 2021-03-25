After Installation
==================

Once you setup your server either via `manual installation <./manual_installation.html>`_
or `docker installation <./docker_installation.html>`_, you will need to setup Vigilio.

Initial Setup
-------------

Go to ``http://localhost:8000`` (default) for docker installation or ``http://your-server-address``
for manual installation. You will be presented with a log in page. Use the credentials that you created
or ``admin`` ``adminadmin`` depending on which method you installed Vigilio.

1. Change the default password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you installed manually, this page will not be shown to you. You can skip to the next step.

If you installed Vigilio via Docker, upon logging in, you will be presented with initial setup process. The first step being the
password change. Set a new password containing at least 8 characters.

Upon setting a new password, you will be forwarded to log in screen again. Log in as admin, using
your newly created password.

2. Setting up MovieDB connection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The next page will ask you to paste your MovieDB API key. You can
`click here <https://developers.themoviedb.org/3/getting-started/introduction>`_
to see the instructions on how to get your API key. After creating your key, copy it and paste it
to the initial setup page of your Vigilio. The system will try checking if the entered API key works.
Upon success, you will be redirected to the next screen.

3. Subtitle language preferences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The next page will ask you to set subtitle languages. If you do not want Vigilio to install subtitles,
you can press on `Skip` button. You can choose the languages you want Vigilio to download from the list
by clicking on them. The selected languages should appear on the screen as selected.

    .. warning:: Selecting many languages may result in performance hit.


After saving your subtitle preferences, you will be directed to the main page.

Setting up search sources
-------------------------

After reaching the index page, you probably will see a text stating ``There are no movies`` and upon
clicking the link below `Add a movie` you will see under `Search` tag that ``There are no sources``

Vigilio comes with no sources to search content with. It is up to you to add them. Thankfully, adding
new sources is easy. Clicking the link on `Please add sources in the settings.` will take you the sources
tab in the settings. By clicking the button `Add a source`, you will see two input boxes.

You can head to `Vigilio sources <https://vigiliosources.docaine.com/>`_ to see the available sources. The
sources in this website is user generated. Be sure to check whether it contains non-legal content or not. The
responsibility of adding the source is on you.

When you choose a source in `Vigilio sources <https://vigiliosources.docaine.com/>`_, click on `Copy Source`
button. Return back to Vigilio and paste it to `*Copy the source` input. You can name this source whatever
you want. Provided that the name is less than 50 characters.

This process seems to require several steps but you will most likely have to do this only once. After creating
a new source. You can head to **Manage -> Add Movie**. Now you can search movies by title (or whatever the
source allows you to search with).

Change qbittorrent password
---------------------------

It is strongly recommended that you change the default qbittorrent password. It is important that you do this
when there is no torrent activity. Head over to ``http://localhost:8080`` and login to your qbittorrent web UI with

| Username ``admin``
| Password ``adminadmin``

Head to **Tools -> Options... -> Web UI** and enter a new password to the input area `Password` and scroll
down to the bottom and click **Save**.

After changing the password, head over to Vigilio. **Manage -> Settings -> Environment Settings** and
change `QBITTORRENT_PASSWORD`.

This should make things a tad bit safer. However, it is highly recommended that you block 8080 port so it is
only available on your server/computer and not to the outside world.

Using VPN
---------

| Using a VPN is highly encouraged. You can either run a VPN connection server wide or you can set SOCKET5 at
    qbittorrent settings:
| **Tools -> Options... -> Connection -> Proxy Server**
