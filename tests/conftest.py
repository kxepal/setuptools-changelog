#
# Copyright 2017, Alexander Shorin
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

import datetime
import os

import pytest
import setuptools

from setuptools_changelog.changelog import ChangeLog


@pytest.fixture()
def distribution():
    return setuptools.Distribution({
        'author': 'John Doe',
        'author_email': 'john.doe@example.com',
        'description': 'long story short',
        'install_requires': ['test==1.2.3'],
        'keywords': ['foo', 'bar', 'baz'],
        'license': 'BSD',
        'long_description': 'long story long',
        'name': 'simple',
        'url': 'https://example.com',
        'version': '0.0.0',
    })


@pytest.fixture()
def make_changelog(distribution):  # pylint: disable=redefined-outer-name
    command = ChangeLog(distribution)
    command.major_changes_types = {
        'breaking': 'Breaking Changes'
    }
    command.minor_changes_types = {
        'feature': 'New Features'
    }
    command.patch_changes_types = {
        'bug': 'Bug Fixes'
    }

    def _make_changelog(**kwargs):
        for key, value in kwargs.items():
            assert hasattr(command, key)
            setattr(command, key, value)
        command.finalize_options()
        return command

    return _make_changelog


@pytest.fixture(scope='session')
def major_changes():
    return os.path.join(os.path.dirname(__file__), 'major')


@pytest.fixture(scope='session')
def minor_changes():
    return os.path.join(os.path.dirname(__file__), 'minor')


@pytest.fixture(scope='session')
def patch_changes():
    return os.path.join(os.path.dirname(__file__), 'patch')


@pytest.fixture(scope='session')
def no_changes():
    return os.path.join(os.path.dirname(__file__), 'empty')


@pytest.fixture(scope='session')
def today():
    return datetime.datetime.now().date()
