..
.. Copyright 2018, Alexander Shorin
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
.. http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
..

Setuptools Changelog
====================

This project is a setuptools extension which helps to generate change logs from
fragments. This way of changelog management is conflict free, what is extremely
helpful for PR/MR driven workflow.


Requirements
------------

- Python 2.7, 3.5+;
- setuptools (31+, but the latest release is better);
- Your project follows `Semantic Versioning`_ or uses it simplified (``X.Y``
  version) form;


Usage
-----

0. Add `setuptools-changelog` as development dependency to your project;
1. Create `changelog.d` directory in your project root directory
   (where `setup.py` is located)
2. Create there fragments files according the changes you made. Fragments files
   have the following format::

    {name}.{type}.{ext}

   Where:

   - ``name``: fragment name. If it *starts* with a number and you have
     issue tracker specified, this number will turn into issue reference
     automatically. Otherwise there could be just some mnemonic name to
     simplify navigation.

   - ``type``: fragment type. By default, the following types are available

     - Major changes:

       - ``epic``: Massive epic change that completely changes underlying
         project platform. This could be a shift to completely new base
         library, framework, etc. Epic changes are very rare and are the reason
         for major release.

       - ``breaking``: Breaking change means changes in the project
         **public API** which makes old code incompatible with them.
         Incompatibility means that things were removed or their behavior had
         changed.

     - Minor changes:

       - ``security``: This is an important security fix. Users must update
         ASAP. If security fix causes breaking change, two separate changelog
         fragments should be issued.

       - ``deprecation``: Deprecations are friendly warnings about upcoming
         breaking changes in the public API.

       - ``feature``: New features brings something to project and they must be
         available for users via public API.

     - Patch changes:

       - ``bug``: When something works in the way it's not expected or supposed
         to we do a bug fix.

       - ``improvement``: This could be speed optimizations, internals
         refactoring, making code more stable etc. Improvements are never
         changes the existed behaviour or public API.

       - ``build``: Changes, related to project build routines, packaging,
         etc.

       - ``doc``: Documentation updates, clarifications, typo fixes, etc.

       - ``test``: Work around project testing, test suite, CI, etc.

       - ``misc``: Misc changes which doesn't suites any existed category.
         For instance, they could be announcements about project life: new
         committers, endorsements, etc.

   - ``ext``: file extension. Currently, we support only `rst` one.

3. You can always preview changelog via::

      python setup.py changelog

4. Once you'll be ready for release, you can update your changelog file like::

      python setup.py changelog --update=CHANGELOG.rst

   This command will *prepend* generated changelog to your file.

5. Review your changelog file content and everything is fine commit it and
   remove fragments::

      git rm changelog.d/*
      git commit CHANGELOG.rst changelog.d/

Example configuration for ``setup.cfg`` using defaults:

.. code::

    [changelog]
    changelog_fragments_path = changelog.d
    major_changes_types =
        epic = Epic Changes
        breaking = Breaking Changes
        removal = Breaking Changes
    minor_changes_types =
        security = Security Fixes
        deprecation = Deprecations
        feature = New Features
    patch_changes_types =
        bug = Bug Fixes
        bugfix = Bug Fixes
        improvement = Improvements
        build = Build
        doc = Documentation
        test = Tests Suite
        misc = Miscellaneous


Automatic version generation
----------------------------

If your project follows `Semantic Versioning`_ strategy, you can achieve not
just changelog generation, but also automatic version management depending on
changes it has.


Integration with `towncrier`_
-----------------------------

This project was started because there are several reasons for me to not use
`towncrier`_ for changelog management. But

.. epigraph::

   Why have enemies, when you can have friends?

   -- King Arthur: Legend of the Sword

Instead, we can support fragments, made for towncrier with the following
config:

.. code::

    [changelog]
    changelog_fragments_path = changelog.d
    major_changes_types =
        removal = Breaking Changes
    minor_changes_types =
        feature = New Features
    patch_changes_types =
        bugfix = Bug Fixes
        doc = Documentation
        misc = Miscellaneous
    use_towncrier = true

And that's it!


.. _Semantic Versioning: https://semver.org/
.. _towncrier: https://github.com/hawkowl/towncrier
