=========
CHANGELOG
=========


Next
====

New feature
-----------

By pressing "*" you can select-and-move in a single operation, combining
"x" and "down arrow".

Python-support
--------------

We stopped supporting EoL Pythons (3.7, 3.8, 3.9), and added support for
Python 3.12, 3.13, and 3.14. We also dropped support for 3.10 a little
early as this allowed us to remove a compatibility shim.

Performance
-----------

A lot of things used to happen every time through the main event loop,
which affected performance.

* DNS lookups are now cached. The best solution is probably to leave the
  lookup to the zino server every time a DNS lookup is relevant to the
  clients, instead of having it depend on case type.
* Configuring colors now only happens once, before anything is written
  to the screen. This also makes it possible to use colors outside of
  the case list.
* The list of visible cases is now only recalculated when necessary: on
  adding a new case, deleting a case, filtering cases, or moving to
  previous or next page.
* When filtering we precompile the filter after it has changed instead
  of compiling just in time 5 times for each case every time we sort.

When there are thousands of cases it no longer takes several seconds to
start up, or move between cases.

Bugfixes
--------

* The list of visible cases was mutated all over the place triggering
  a crash to the shell. This list is now paged, making moving around in
  the list much safer especially when a case is deleted. [Github#1,
  Github#3]
* The filter window supports Python regular expressions, but if an
  invalid expression was inputted we crashed to the shell. Now we show
  an error mesage instead and allow for editing the pattern when it is
  invalid. [Github#2]
* Our pyproject.toml had to be updated to handle a poorly planned
  change to the upstream Python packaging milieu. [Github#7]
* We no longer crash to shell when the zino server dies with a cryptic
  message, now we exit cleanly with an actionable message instead.
  [Github#4]

Documentation
-------------

This changelog was added. [Github#6]

There are now some docs hosted at the main Zino docs site:
`Zino clients: cuRitz <https://zino.readthedocs.io/en/latest/clients/curitz.html>`_

Dependencies
------------

We're no longer locked to an old zinolib.

Testing
-------

Now using pytest.

0.9.22
======

Updated the most important dependency, zinolib.

0.9.21
======

Test on Python 3.12, fine-tuned some dependencies, improved the README
with a "Configuration"-section and a "Running"-section.

0.9.20
======

First version handled by the CNaaS-dev team. No new real features.
Changed how the config object is built and passed around to cut down on
globals.

Mainly adding boilerplatei: set up for CI/CD, linting, clean up, switch
to pyproject.toml from setup.py, and other prep for release on PyPI.
