..
.. Copyright 2017, Alexander Shorin
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
- setuptools (modern versions);
- Your project follows `Semantic Versioning`_ or uses it simplified (``X.Y``
  version) form;


Automatic version generation
----------------------------

If your project follows `Semantic Versioning`_ strategy, you can achieve not
just changelog generation, but also automatic version management depending on
changes it has.


Why not `towncrier`_?
---------------------

Mostly, by personal reasons:

1. ``pyproject.toml`` is cool, but still far future. I don't want to have yet
   another project configuration file to support. This project is an extension
   for setuptools and integrates with it transparently.

2. I like when file extension reflects it format and is not a tool specific
   magic.

3. Sometimes, changes comes without issue number. These should be rendered
   as is while fragment name is used to simplify navigation.

4. Personally, I don't keep in mind all the issue numbers and remember what
   changes when, so having some short mnemonic in filename helps a lot in
   navigation.

5. I'd like to cooperate fragment-based changelog management with automatic
   project version control. For instance, if we did (and document) breaking
   change, next version must have major number bump. Can I do this with
   `towncrier`_? Unlikely.

N. Finally, why not? (:


.. _Semantic Versioning: https://semver.org/
.. _towncrier: https://github.com/hawkowl/towncrier
