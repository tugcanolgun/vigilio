How to use
==========

This page aims to explain features of Vigilio and how to use them.

How to add a search source
--------------------------

| Vigilio does not come with a search source. You need to add a source to be able to search movies and download them
    with one click. In order to add new sources, head to
| **Manage -> Settings -> Search Sources**

Here you can see and delete your existing search sources.

If you want to add a new source, click on **Add a source** button. On the page, it should show you a link to find
sources for Vigilio. You can find sources `here <https://vigiliosources.docaine.com/>`_

.. warning::

    Sources may contain non-public domain movies and it may be illegal to acquire such movies in
    your country. Be cautious which source to choose.

.. figure:: https://user-images.githubusercontent.com/18149492/112537994-a6132d80-8daf-11eb-9a32-316eb33a51be.jpg
   :align: center

   *Example vigilio source page*

You can test the source by clicking **Test** button and entering a search text such as movie title. If everything is okay,
you can click **Copy source** button to copy the source.

Go back to vigilio add source page, paste the source to second field *(*Copy the source)*

Enter a name for this source and click **Save**

| Now you should be able to search movies on
| **Manage -> Add Movie -> Search**

Add movies
----------

There are 3 ways to add movies to Vigilio

1. Add by searching
^^^^^^^^^^^^^^^^^^^

**Manage -> Add Movie -> Search**

Search a movie, click on **Download&Add** to add movie.

You can see the process of added movie at **Manage -> Background Management**

2. Add by providing torrent source and imdb id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Manage -> Add Movie -> Add Manually**

Copy IMDB id or IMDB link to the first field

``tt0050083`` or ``https://www.imdb.com/title/tt0050083/``

Copy a magnet link or .torrent file link to the second field *Copy a torrent magnet or link*

| ``https://some-url/some-category/content.torrent``
| or
| ``magnet:?xt=urn:btih:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA&dn=Some.Content``

You can see the process of added movie at **Manage -> Background Management**

3. Add by manually adding existing movies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is useful to add movies that are already on your system. You need to give the information manually.
Copy the movie you want to add to ``data/downloads`` under your vigilio folder.

Head to the ``admin`` panel. It is at ``http://localhost:8000/admin``.

Login to the page and head to **Stream -> Movies** and click on **ADD MOVIE** button.

Fill the fields with the movie information and add the plus button next to **Movie content** section to add the movie
you have to this movie.

| Upon clicking a new window should open. You can just put a random string to the **Torrent source** field as this is
    a mandatory field. In this window the two mandatory fields are:
| **Full path**      Eg: ``/home/users/vigilio/data/downloads/My.Movie/movie.mp4``
| **File extension** Eg: ``.mp4``

You should consider entering resolution information too so the movie cards can show **4K, HD, HDTV** badges.

Tick the **Is ready** field and click on **SAVE**

Once this window is closed, you should lastly tick the **Is ready** field on movie form as well and you can click
**SAVE** button.

This should be it. Your movie should now show up on the main page and if the movie container is correct, it should
play without a problem.

Deleting a movie
----------------

Head to **Manage** and find the movie or you can click on gear icon on movie posters. Once you are
at the movie details page, under *Management tools* you can find the row *Remove this movie and everything related to it*
and next to it there is a clickable text **Click here to reveal the button.**. Once clicked, this text should
turn into **Delete this movie** button. You can use this button to delete this movie. This will delete the following:

* Movie files, including different resolutions and versions.
* Subtitles.
* Torrent entries, if exists.
* Background processes.
* Database entries including user histories.


Adding, removing subtitle languages
-----------------------------------

**Manage -> Settings -> Subtitle Languages**

You can add languages by searching or remove languages by clicking the x button next to the selected ones. You need to
press **Save** button to save these settings.

Download subtitles
------------------

When adding a movie, subtitles should automatically be added but you may want to repeat these when,

* You change your language settings.
* You add a movie by manually through admin panel.

Head to **Manage -> Settings -> Redownload Subtitles**

Select the movies you want subtitles to be re-downloaded and click **Redownload Subtitles** button.

Changing environment settings
-----------------------------

**Manage -> Settings -> Environment Settings**

.. warning::

    Changing these settings may cause the system to not work properly. Be very cautious.

Some of these settings requires the system to be restarted to take affect.

You can change ``ALLOWED_URLS`` with your domain name to increase security.

