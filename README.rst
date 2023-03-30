======
curitz
======

Python curses package to interface with Zino.

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
