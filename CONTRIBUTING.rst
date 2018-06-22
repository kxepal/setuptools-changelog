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


Contributing
============

1. Fork and git clone the project;
2. Create virtual environment::

   make venv

3. Activate virtual environment::

   source venv/bin/activate

4. Install project in development mode::

   make develop

5. Create a new git branch about what the changes would be made::

       git checkout --branch changelog-generation-bugfix

  If you're fixing an issue, start the branch name with it number::

        git checkout --branch 42-docs-typo

6. Write the code and tests and ensure that everything is alright::

    make check

7. Generate changelog fragment::

        make fragment name=42-typo type=doc

   If there is no issue about what you're working on, set the name as short
   mnemonic name::

        make fragment name=readme-typo type=doc

   If your change is a single commit change, then use `fragment-amend`
   instead::

        make fragment-amend name=readme-typo type=doc

   This will squash changelog fragment with your last (and single one) commit.

8. Push the changes and create a new Pull Request.

9. ...

10. PROFIT! And thank you!
