=========
CHANGELOG
=========

1.0.0 2026-09-28
================

Main changes:

* one new feature, pressing "*" for select-and-move
* MANY performance improvements
* Many errors leading to crashes are handled better

There are now some docs hosted at the main Zino docs site:
`Zino clients: cuRitz <https://zino.readthedocs.io/en/latest/clients/curitz.html>`_

Added
-----

* By pressing "*" you can select-and-move in a single operation,
  combining "x" and "down arrow".
* Support was added for Python 3.13, and 3.14.
* This changelog was added. [https://github.com/Uninett/curitz/issues/6]

Removed
-------

* We stopped supporting EoL Pythons (3.7, 3.8, 3.9). We also dropped
  support for 3.10 a little early as this allowed us to remove
  a compatibility shim.

Changed
-------

* We're no longer locked to an old zinolib.
* Unittest testrunner and tests were replaced with pytest.
* A lot of things used to happen every time through the main event loop,
  which affected performance. When there were thousands of cases it
  would take several seconds to start up, or move between cases.

  * DNS lookups are now always cached. The correct solution is probably
    to do all lookups on the zino server so that all clients always work
    with the same data.
  * The list of visible cases is now only recalculated when necessary:
    on adding a new case, deleting a case, filtering cases, or moving to
    previous or next page.
  * Configuring colors now only happens once, before anything is written
    to the screen. This also makes it possible to use colors outside of
    the case list.
  * When filtering we precompile the filter after it has changed instead
    of several times per entry to sort and filter.

Fixes
-----

* Our pyproject.toml had to be updated to handle a poorly planned change
  to the upstream Python packaging milieu.
  [https://github.com/Uninett/curitz/issues/7]
* Several crashes to console were fixed

  * The list of visible cases was mutated all over the place triggering
    a crash. This list is now paged, making moving around in the list
    much safer especially when a case is deleted.
    [https://github.com/Uninett/curitz/issues/1]
    [https://github.com/Uninett/curitz/issues/3]
  * The filter window supports Python regular expressions. Invalid
    expression were not hadled and led to a crash. Now we show an error
    mesage instead and allow for editing the pattern when it is invalid.
    [https://github.com/Uninett/curitz/issues/2]
  * If the zino server dies with a cryptic message, we now exit cleanly
    with an actionable message instead of dumping a generic traceback.
    [https://github.com/Uninett/curitz/issues/4]


0.9.22 2025-07-24
=================

Mini-release.

Changed
-------

* Updated the most important dependency, zinolib.

0.9.21 2024-04-12
=================

Mini-release.

Added
-----

* Test on Python 3.12
* Document how to configure and run curitz in README

Changed
-------

* Set bounds on what zinolib versions to depend on

0.9.20 2023-03-31
=================

First version on PyPI.

First version handled by the CNaaS-dev team. No new real features,
mostly DevEx changes.

Changed
-------

* Reorganized the code, all code in /src
* Split out non-UI code to a separate project and repo: zinolib
* Move free floating global config variables to a non-global config
  object
* Switched from setup.py to pyproject.toml, prepping for
  a release on PyPI
* Linted everything with ruff
* Reformatted code with black

Added
-----

* Set up unit testing with tox
* Set up pre-commit for some linting
* Added Makefile for cleaning
* Added installation instructions to README
* Added license
* Set up testing on Github

Removed
-------

* Dropped support for Pythons older than 3.7
