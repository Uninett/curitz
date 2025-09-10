======
curitz
======

*curitz* is a CUrses-based Remote Interface To Zino, i.e. a terminal-based user
interface to interact with a Zino server.

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
``my.zino.server.com``, authenticated as ``USER_1``.

The bottom four lines are optional. They are an example of how to configure
alternative servers. Running ``curitz`` with the ``/-``-argument would connect
to the alternative server::

    $ curitz -p ALTERNATE

This would connect to ``alternative.zino.server.com``, authenticated as ``USER_2``.

Installing
==========

From PyPI
---------

curitz is available on PyPI. The quickest way to install it is therefore using
some variation of ``pip install``.  We recommend installing it into your own
user environment in order to not interfere with system packages, like so::

    pip install --user curitz

This should normally put the binary and library under ``.local`` on Linux.

If you have the ``uv`` tool available on your system, you can install and run
curitz directly by issuing the command::

    uvx curitz

From source
-----------

If installing directly from a clone of this source code repository, you can
install curitz (again, we recommend installing to your own user environment)::

    pip install --user .


Running
=======

After installing (and assuming your ``PATH`` environment variable is set
correctly), the terminal program ``curitz`` will be available to run.

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

Development
===========

Some minimal pre-commit hooks are included, install by running
``pre-commit install``.

See the file `.git-blame-ignore-revs` for commits to ignore when running
`git blame`. Use it like so::

    git blame --ignore-revs-file .git-blame-ignore-revs FILE
