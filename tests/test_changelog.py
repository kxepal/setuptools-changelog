#
# Copyright 2018, Alexander Shorin
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import pytest


def test_major_changes(make_changelog, major_changes, capsys, today):
    changelog = make_changelog(changelog_fragments_path=major_changes)
    changelog.run()
    stdout, _ = capsys.readouterr()
    assert stdout == '''
1.0.0 ({})
==================

Breaking Changes
----------------
- #1: This is a breaking change.
'''.lstrip().format(
        today,
    )


def test_minor_changes(make_changelog, minor_changes, capsys, today):
    changelog = make_changelog(changelog_fragments_path=minor_changes)
    changelog.run()
    stdout, _ = capsys.readouterr()
    assert stdout == '''
0.1.0 ({})
==================

New Features
------------
- New cool feature!

Bug Fixes
---------
- Fix zero division issue.

  This happens when we pass second parameter as zero. Now in this case we
  return default value instead of raising division exception.
'''.lstrip().format(
        today,
    )


def test_patch_changes(make_changelog, patch_changes, capsys, today):
    changelog = make_changelog(
        changelog_fragments_path=patch_changes,
        issue_tracker='https://github.com/example/project/issues/%s'
    )
    changelog.run()
    stdout, _ = capsys.readouterr()
    assert stdout == '''
0.0.1 ({})
==================

Bug Fixes
---------
- `#42`_: Finally flaky bug get fixed.

.. _#42: https://github.com/example/project/issues/42
'''.lstrip().format(
        today,
    )


def test_no_changes(make_changelog, no_changes):
    changelog = make_changelog(
        changelog_fragments_path=no_changes,
        next_version=True
    )
    with pytest.raises(SystemExit):
        changelog.run()


def test_next_major_version(make_changelog, major_changes, capsys):
    changelog = make_changelog(
        changelog_fragments_path=major_changes,
        next_version=True
    )
    changelog.run()
    stdout, _ = capsys.readouterr()
    assert stdout == '1.0.0\n'


def test_next_minor_version(make_changelog, minor_changes, capsys):
    changelog = make_changelog(
        changelog_fragments_path=minor_changes,
        next_version=True
    )
    changelog.run()
    stdout, _ = capsys.readouterr()
    assert stdout == '0.1.0\n'


def test_next_patch_version(make_changelog, patch_changes, capsys):
    changelog = make_changelog(
        changelog_fragments_path=patch_changes,
        next_version=True
    )
    changelog.run()
    stdout, _ = capsys.readouterr()
    assert stdout == '0.0.1\n'
