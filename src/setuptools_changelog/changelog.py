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

import datetime
import os
import re
import sys
from collections import OrderedDict, namedtuple
from itertools import chain, groupby

import semver
from setuptools import Command


try:
    from textwrap import indent
    from urllib.parse import urlparse
except ImportError:  # pragma: no cover
    from urlparse import urlparse

    # This function was borrowed from Python 3.6 sources.
    def indent(text, prefix, predicate=None):
        if predicate is None:
            def _predicate(line):
                return line.strip()
            predicate = _predicate  # Pylint error workaround

        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if predicate(line) else line)

        return ''.join(prefixed_lines())


DEFAULT_CHANGELOG_FRAGMENTS_PATH = 'changelog.d'
DEFAULT_MAJOR_CHANGES_TYPES = OrderedDict([
    ('epic', 'Epic Changes'),
    ('breaking', 'Breaking Changes'),
])
DEFAULT_MINOR_CHANGES_TYPES = OrderedDict([
    ('security', 'Security Fixes'),
    ('deprecation', 'Deprecations'),
    ('removal', 'Deprecations'),
    ('feature', 'New Features'),
])
DEFAULT_PATCH_CHANGES_TYPES = OrderedDict([
    ('bug', 'Bug Fixes'),
    ('bugfix', 'Bug Fixes'),
    ('improvement', 'Improvements'),
    ('build', 'Build'),
    ('doc', 'Documentation'),
    ('test', 'Tests Suite'),
    ('misc', 'Miscellaneous'),
])


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


class TowncrierFragment(Fragment):
    __slots__ = ()

    @classmethod
    def from_path(cls, path):
        try:
            name, type_ = os.path.basename(path).rsplit('.')
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
        ('next-version', None,
         'Prints next release version to stdout.'),
        ('use-towncrier', None,
         'Reuses fragments made for towncrier.'),
        ('update=', None,
         'Prepends generated changelog to specified file.'),
    ]
    boolean_options = [
        'next-version',
    ]

    changelog_fragments_path = None
    issue_pattern = r'\A([0-9]+)'
    issue_prefix = '#'
    issue_tracker = None
    all_changes_types = None
    major_changes_types = None
    minor_changes_types = None
    patch_changes_types = None
    next_version = False
    update = None
    use_towncrier = False

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
        if self.changelog_fragments_path is None:
            self.changelog_fragments_path = DEFAULT_CHANGELOG_FRAGMENTS_PATH

        self.major_changes_types = self._parse_changes_types(
            self.major_changes_types,
            DEFAULT_MAJOR_CHANGES_TYPES,
        )
        self.minor_changes_types = self._parse_changes_types(
            self.minor_changes_types,
            DEFAULT_MINOR_CHANGES_TYPES,
        )
        self.patch_changes_types = self._parse_changes_types(
            self.patch_changes_types,
            DEFAULT_PATCH_CHANGES_TYPES,
        )
        if self.patch_changes_types and not self.minor_changes_types:
            raise RuntimeError(
                'Patch changes are defined while minor are not.'
            )

        self.all_changes_types = {}
        self.all_changes_types.update(self.major_changes_types)
        self.all_changes_types.update(self.minor_changes_types)
        self.all_changes_types.update(self.patch_changes_types)

    def _parse_changes_types(self, changes_types, default):
        if isinstance(changes_types, dict):
            return changes_types

        if changes_types is None:
            return default

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

        if self.use_towncrier:
            fragments = [
                TowncrierFragment.from_path(os.path.join(base_path, item))
                for item in items if not item.startswith('.')
            ]
        else:
            fragments = [
                Fragment.from_path(os.path.join(base_path, item))
                for item in items if item.endswith('.rst')
            ]

        if not fragments:
            self.warn('No fragments found in {} directory'
                      ''.format(self.changelog_fragments_path))
            sys.exit(1)

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

        if self.next_version:
            print(next_version)
            return

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
                    if self.issue_tracker is not None:
                        issue_formatted = '`{}`_: '.format(key)
                        reference = '.. _{}: {}'.format(
                            key,
                            self.issue_tracker % issue_number,
                        )
                    else:
                        issue_formatted, reference = key + ': ', None
                else:
                    issue_formatted, reference = '', None

                chunk = '- {}{}'.format(
                    issue_formatted,
                    indent(fragment.body, '  ').strip()
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

        if self.update is None:
            print(new_changes.strip())
        else:
            changelog_path = self.update  # rename for readability
            if os.path.exists(changelog_path):
                with open(changelog_path) as fobj:
                    content = fobj.read()
            else:
                content = ''
            with open(changelog_path, 'w') as fobj:
                fobj.write(new_changes + '\n' + content)
