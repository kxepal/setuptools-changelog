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


PN = `python setup.py -q --name`
PV = `python setup.py -q --version`
SHELL = /bin/sh
SPHINXOPTS ?= -n -W


.PHONY: all
all: help


.PHONY: changelog
# target: changelog - Prints out upcoming release changelog
changelog:
	@python setup.py -q changelog


.PHONY: check
# target: check - Checks project with the tests, linters and the rest tools
check: check-lint check-coverage


.PHONY: check-coverage
# target: check-coverage - Runs tests with coverage
check-coverage:
	@python -m pytest --cov


.PHONY: check-lint
# target: check-lint - Check source code with linters
check-lint:
	@python -m pytest -m 'flake8 or isort or pylint' \
	    --flake8 \
	    --isort \
	    --pylint --pylint-error-types=WEF --pylint-rcfile=.pylintrc


.PHONY: clean
# target: clean - Removes intermediate and generated files
clean:
	@find . -type f -name '*.py[co]' -delete
	@find . -type d -name '__pycache__' -delete
	@rm -f .coverage
	@rm -rf {build,htmlcov,cover,coverage}
	@rm -rf src/*.egg-info
	@rm -f RELEASE
	@rm -f VERSION
	@python setup.py clean


.PHONY: commit-changelog
commit-changelog:
	@python setup.py changelog --update=CHANGELOG.rst
	@git rm changelog.d/*.rst
	@git commit CHANGELOG.rst changelog.d/*.rst -m "Release `cat VERSION`"


.PHONY: coverage-report
# target: coverage-report - Prints coverage report
coverage-report:
	@python -m coverage report


.PHONY: coverage-html
# target: coverage-html - Generates coverage HTML report
coverage-html:
	@python -m coverage html


.PHONY: develop
# target: develop - Installs package in develop mode
develop:
	@python -m pip install --upgrade pip setuptools wheel
	@python -m pip install -e .[develop]


.PHONY: dist
dist: sdist wheel


.PHONY: distcheck
# target: distcheck - Verifies distributed artifacts
distcheck: sdist
	@mkdir -p dist/$(PN)
	@tar -xf dist/$(PN)-$(PV).tar.gz -C dist/$(PN) --strip-components=1
	@$(MAKE) -C dist/$(PN) venv
	@. dist/$(PN)/venv/bin/activate && pip install --upgrade setuptools
	@. dist/$(PN)/venv/bin/activate && $(MAKE) -C dist/$(PN) develop
	@. dist/$(PN)/venv/bin/activate && $(MAKE) -C dist/$(PN) check
	@rm -rf dist/$(PN)


.PHONY: ensure-clean
ensure-clean:
	@git diff --exit-code
	@git diff --cached --exit-code


.PHONY: ensure-tag
ensure-tag:
	@git describe --exact-match --tags $(git log -n1 --pretty='%h')


.PHONY: format
# target: format - Automatically formats the code according the common style
format:
	@python -m isort.main -rc setup.py src/ tests/
	@python -m autoflake -i -r \
	    --remove-all-unused-imports \
	    --remove-unused-variables \
	    setup.py \
	    src/ \
	    tests/


.PHONY: format-diff
# target: format-diff - Shows what will be done by `make format`
format-diff:
	@python -m isort.main -df -rc setup.py src/ tests/
	@python -m autoflake -r \
	    --remove-all-unused-imports \
	    --remove-unused-variables \
	    setup.py \
	    src/ \
	    tests/

.PHONY: help
# target: help - Prints this help
help:
	@egrep "^# target: " Makefile \
		| sed -e 's/^# target: //g' \
		| sort -h \
		| awk '{printf("    %-16s", $$1); $$1=$$2=""; print "-" $$0}'


.PHONY: install
# target: install - Install the project
install:
	@pip install .


.PHONY: pylint
# target: pylint - Generates pylint report
pylint:
	@python -m pylint setup.py src/ tests/


.PHONY: purge
# target: purge - Removes all unversioned files and resets working copy
purge:
	@git reset --hard HEAD
	@git clean -xdff


.PHONY: release
# target: release - Makes a new release
release: ensure-clean \
         distcheck \
         release-notes \
         dist \
         commit-changelog \
         tag-release


.PHONY: release-notes
release-notes:
	@python setup.py -q changelog > RELEASE
	@$(EDITOR) RELEASE


.PHONY: sdist
# target: sdist - Builds source distribution artifact
sdist: clean
	@python setup.py sdist


.PHONY: tag-release
tag-release:
	@git tag -F RELEASE `cat VERSION`


# target: venv - Creates virtual environment
venv:
	@python -m venv venv


.PHONY: version
# target: version - Generates and prints project version in PEP-440 format
version: VERSION
	@cat VERSION
VERSION:
	@git describe --always --tags | sed -r 's/^(.*)-(.*)-(.*)/\1.\2+\3/' > $@


.PHONY: uninstall
# target: uninstall - Delete project installation
uninstall:
	@pip uninstall $(PN)


.PHONY: upload
# target: upload - Uploads artifacts on PyPI
upload: ensure-clean ensure-tag sdist wheel
	@python setup.py sdist bdist_wheel register upload


.PHONY: wheel
# target: wheel - Builds wheel artifact
wheel: clean
	@python setup.py bdist_wheel
