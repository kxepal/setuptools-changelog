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
import re
import sys
from collections import OrderedDict, namedtuple
from distutils.errors import DistutilsOptionError
from itertools import chain, groupby
from urllib.parse import urlparse

import semver
from setuptools import Command


class InvalidFragment(RuntimeError):
    def __init__(self, path, msg):
        super(InvalidFragment, self).__init__('`{}`. {}'.format(path, msg))


class Fragment(namedtuple('Fragment', ['path', 'name', 'body', 'type'])):
    __slots__ = ()

    @classmethod
    def from_path(cls, path):
        try:
            name, type_, _ = os.path.basename(path).rsplit('.')
        except ValueError:
            raise InvalidFragment(
                path,
                'Fragment filename name must have name, fragment type and'
                ' proper extension parts joined by a dot.',
            )
        else:
            with open(path) as fobj:
                body = fobj.read()
            return cls(path, name, body, type_)


class ChangeLog(Command):
    user_options = [
        ('changelog-fragments-path=', None,
         'Path to changelog fragments.'),
        ('issue-pattern=', None,
         'Issue regexp pattern. Those who matches will be translated into'
         ' links. Those who don\'t - will be ignored.'),
        ('issue-prefix=', None,
         'Prefix string tso add to issue name.'),
        ('issue-url=', None,
         'URL of issue tracker to use for issue references. By default it'
         ' tries to detect GitHub usage to build correct issue URL. Custom URL'
         ' may be be used in format: http://host/path/%s'
         ' where %s is a placeholder for issue number.'),
    ]

    changelog_fragments_path = None
    issue_pattern = r'\A([0-9]+)'
    issue_prefix = '#'
    issue_tracker = None
    all_changes_types = None
    major_changes_types = None
    minor_changes_types = None
    patch_changes_types = None

    def initialize_options(self):
        url = self.distribution.get_url().strip('/')
        hostname = urlparse(url).hostname
        if hostname is None:
            self.issue_tracker = None
        elif 'github.com' in hostname:
            self.issue_tracker = url + '/issues/%s'
        else:
            self.issue_tracker = None  # will be set via setuptools config

    def finalize_options(self):
        assert self.changelog_fragments_path is not None
        self.major_changes_types = self._parse_changes_types(
            self.major_changes_types
        )
        self.minor_changes_types = self._parse_changes_types(
            self.minor_changes_types
        )
        self.patch_changes_types = self._parse_changes_types(
            self.patch_changes_types
        )

        if self.patch_changes_types and not self.minor_changes_types:
            raise DistutilsOptionError(
                'Patch changes are defined while minor are not.'
            )

        self.all_changes_types = {}
        self.all_changes_types.update(self.major_changes_types)
        self.all_changes_types.update(self.minor_changes_types)
        self.all_changes_types.update(self.patch_changes_types)

    def _parse_changes_types(self, changes_types):
        if isinstance(changes_types, dict):
            return changes_types

        changes_types = changes_types.strip()
        if not changes_types:
            return {}

        acc = []
        for line in changes_types.splitlines():
            key, value = map(str.strip, line.split('=', 1))
            acc.append((key, value))
        return OrderedDict(acc)

    def run(self):
        if not os.path.exists(self.changelog_fragments_path):
            self.warn('{} directory does not exists'
                      ''.format(self.changelog_fragments_path))
            sys.exit(1)

        if not os.path.isdir(self.changelog_fragments_path):
            self.warn('{} is not a directory'
                      ''.format(self.changelog_fragments_path))
            sys.exit(1)

        def group_by_type(fragments, known_changes_types):
            def by_type(item):
                return item.type

            def by_order(item):
                try:
                    return known_changes_types.index(by_type(item))
                except ValueError:
                    raise InvalidFragment(
                        item.path,
                        'Unknown fragment type {0.type}.'
                        ' Misconfiguration or just a typo?'
                        ''.format(item)
                    )

            groups = groupby(sorted(fragments, key=by_order), key=by_type)
            return groups

        content = []
        footer = []

        base_path = self.changelog_fragments_path
        items = sorted(os.listdir(base_path))
        fragments = [Fragment.from_path(os.path.join(base_path, item))
                     for item in items if item.endswith('.rst')]

        changes_types = list(chain(
            self.major_changes_types,
            self.minor_changes_types,
            self.patch_changes_types,
        ))

        orig_version = self.distribution.get_version()
        match = re.match(
            r'^(?P<major>(?:0|[1-9][0-9]*))'
            r'\.(?P<minor>(?:0|[1-9][0-9]*))'
            r'(?:\.(?P<patch>(?:0|[1-9][0-9]*)))?',
            orig_version,
            re.VERBOSE,
        )
        if match is None:
            raise RuntimeError('Version {} could not be used for SemVer'
                               ''.format(orig_version))
        groups = match.groupdict()
        qual_version = '.'.join([
            groups['major'], groups['minor'], groups['patch'] or '0'
        ])

        next_version = None
        for chtype, _ in group_by_type(fragments, changes_types):
            if chtype in self.major_changes_types:
                next_version = semver.bump_major(qual_version)
            elif chtype in self.minor_changes_types:
                next_version = semver.bump_minor(qual_version)
            elif chtype in self.patch_changes_types:
                next_version = semver.bump_patch(qual_version)
            break
        assert next_version is not None

        today = datetime.datetime.now().date()
        title = '{} ({})'.format(next_version, today)
        title += '\n' + '=' * len(title)
        content.insert(0, title)

        for chtype, fragments_group in group_by_type(fragments, changes_types):
            header_title = self.all_changes_types[chtype]
            header_line = '-' * len(header_title)

            chunks = []
            references = []
            for fragment in fragments_group:
                match = re.match(self.issue_pattern, fragment.name)
                if match:
                    issue_number = match.group(0)
                    key = '{}{}'.format(self.issue_prefix, issue_number)
                    issue_formatted = '`{}`_: '.format(key)
                    if self.issue_tracker is not None:
                        reference = '.. _{}: {}'.format(
                            key,
                            self.issue_tracker % issue_number,
                        )
                    else:
                        reference = None
                else:
                    issue_formatted, reference = '', None

                chunk = '- {}'.format(issue_formatted) + '\n  '.join(
                    line for line in fragment.body.splitlines()
                )
                chunks.append(chunk)
                references.append(reference)

            section_content = '\n\n'.join(chunks)
            section = '\n'.join([header_title, header_line, section_content])

            content.append(section)
            for reference in references:
                if reference is not None and reference not in footer:
                    footer.append(reference)

        new_changes = '\n\n'.join(content)
        new_changes += '\n\n' + '\n'.join(sorted(footer))

        print(new_changes.strip())