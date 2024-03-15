======
curitz
======

Python curses package to interface with Zino.

Split from internal project PyRitz on 2023-03-30.

Configuration
=============

There needs to be a file ``.ritz.tcl``, conventionally placed in your
home-directory.

Example ``.ritz.tcl``::
    set Secret ZINO1SERVERTOKEN_A
    set User USERNAME_1
    set Server my.zino.server.com
    set Port 8001

    set _Secret(ALTERNATE) ZINO1SERVERTOKEN_B
    set _User(ALTERNATE) USERNAME_2
    set _Server(ALTERNATE) alternative.zino.server.com
    set _Port(ALTERNATE) 8001

The top four lines configures the default server. ``Secret`` and ``User`` is
created by the admin of the zino server. ``Server`` and ``Port`` hopefully
needs no explanation.

Running ``curitz`` without the ``-p``-argument would connect to
"my.zino.server.com", authenticated as USER_1.

The bottom four lines are optional. They are an example of how to configure
alternative servers. Running ``curitz`` with the ``/-``-argument would connect
to the alternative server::

    ``$ curitz -p ALTERNATE``

This would connect to "alternative.zino.server.com", authenticated as USER_2.

Running
=======

After installingOnce it is on your path the terminal program ``curitz`` will be available to run.

Run ``curitz -h`` for info about the available arguments.

Testing
=======

This library is testable with unittests. When testing it starts a Zino emulator
that reponds correctly to requests as the real server would do.

If you have all currently supported pythons in your path, you can test them
all, with an HTML coverage report placed in ``htmlcov/``::

    tox

To test on a specific python other than current, run::

    tox -e py{version}

where ``version`` is of the form "311" for Python 3.11.

Install
=======

To use ``curitz`` we recommend installing it to your local user, for instance
with ``pip`'s ``--user``-flag::

    pip install --user .

if installing from source or::

    pip install --user curitz

if installing from Pypi. This should normally put the binary and library under
``.local`` on Linux.

Development
===========

Some minimal pre-commit hooks are included, install by running
``pre-commit install``.

See the file `.git-blame-ignore-revs` for commits to ignore when running
`git blame`. Use it like so::

    git blame --ignore-revs-file .git-blame-ignore-revs FILE
