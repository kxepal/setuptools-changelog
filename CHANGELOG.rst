1.0.0 (2018-06-17)
==================

Epic Changes
------------
- First public release is an epic change!

New Features
------------
- Set default changelog fragments path and changes types mappings.

- Add ``--next-version`` flag to print out next version to stdout. This should
  help with auto tagging releases.

- Assign generated changelog next release version. Project should follow Semantic
  Versioning strategy or it simplified form (just ``X.Y`` version).

- Support out-of-the-box towncrier fragments types. To generate changelog from
  them, use ``--use-towncrier`` cli option or set ``use_towncrier = true``
  parameter in `setup.cfg`.

- Add ``--update=`` argument to prepend generated changelog to a given file.

Bug Fixes
---------
- Changelog generation shouldn't fail if changes directory contains no fragments.

Build
-----
- Automate release process.

- Generate project changelog as a part of Travis CI build.

- Add `make fragment` helper to generate changelog fragments from git log.

- Drop Python 2.7 build on Travis CI. I'm not interested in it, but if it'll
  be broken - patches welcome!

- Workaround https://github.com/pypa/setuptools/issues/1136

Documentation
-------------
- Add contributing guide

- Update ``README.rst`` file with comprehensive description of each fragment
  type.

- Clarify what is the "modern setuptools versions"

Tests Suite
-----------
- Add some basic tests for changelog and next version generation.

- Workaround https://github.com/PyCQA/pylint/issues/73


