Contribution Guidelines
=======================

First of all, thanks for thinking of contributing to this project! 👏

Following these guidelines helps to communicate that you respect the time of the maintainer and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

Ways to Contribute
------------------

    * Blog or tweet about the project
    * Improve documentation
    * Fix a bug
    * Implement a new feature
    * Discuss potential ways to improve project
    * Improve existing implementation, performance, etc.

Questions & Feature Requests
----------------------------

Feel free to `open a ticket <https://github.com/tugcanolgun/vigilio/issues/new>`_ with your question. Feature requests are also welcome. Describe the feature, why you need it, and how it should work. Please provide as much detail and context as possible.

File a Bug
----------

In case you've encountered a bug, please make sure:

    * You are using the `latest version <https://github.com/tugcanolgun/vigilio/releases>`_.
    * You have read the documentation first, and double-checked your configuration.
    * In your issue description, please include:
        - What you expected to see, and what happened instead.
        - Your operating system and other environment information.
        - As much information as possible, such as the command and configuration used.
        - Interesting logs from a verbose and/or debug run.
        - All steps to reproduce the issue.

Pull Requests
-------------

Pull requests are welcome! If you never created a pull request before, here are some tutorials:

    * `Creating a pull request <https://help.github.com/articles/creating-a-pull-request/>`_
    * `How to Contribute to an Open Source Project on GitHub <https://egghead.io/courses/how-to-contribute-to-an-open-source-project-on-github>`_

Development
-----------

    * Fork this project.
    * Follow instructions for how to run Vigilio for development `here <./development.html>`_.
    * Make sure you added tests to your contribution.
    * Make sure you run the following linters, formatters and test:

.. code-block:: bash

    make pyfix
    make pylint
    make jsfix
    make jslint
    make test

If everything is okay, push your changes and `create a pull request <https://github.com/tugcanolgun/vigilio/compare>`_.
