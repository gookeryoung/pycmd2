FIND_NAME = find . -path './.venv' -prune -o -name
.PHONY: bump clean cov dist doc help init lint pub sync

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

define UPDATE_BUILDDATE_SCRIPT
import datetime
import fileinput
import pathlib
import re
import sys

build_date = datetime.datetime.now().strftime("%Y-%m-%d")
init_file = pathlib.Path.cwd() / "src" / "pycmd2" / "__init__.py"
for line in fileinput.input(init_file, inplace=True):
	if "__build_date__" in line:
		print(f'__build_date__ = "{build_date}"')  # 替换整行
	else:
		print(line, end='')  # 保持原行
print(f"Update __build_date__ -> {build_date}")
endef
export UPDATE_BUILDDATE_SCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"
COVERAGE := coverage
RUFF := uvx ruff
UPDATE_BUILD_DATE := python -c "$$UPDATE_BUILDDATE_SCRIPT"
SPHINX_APIDOC := sphinx-apidoc
SPHINX_BUILD := sphinx-build

bump: ## bump project version using `bump-my-version`. Example: `0.7.7` -> `0.7.8`
	uvx --from bump2version bumpversion patch
	$(UPDATE_BUILD_DATE)

bumpmi: ## bump project version using `bump-my-version`, bump minor version.
	uvx --from bump2version bumpversion minor
	$(UPDATE_BUILD_DATE)

bumpma: ## bump project version using `bump-my-version`, bump major version.
	uvx --from bump2version bumpversion major
	$(UPDATE_BUILD_DATE)

bumpp: bump publish ## bump and publish

clean: ## remove all build, test, coverage and Python artifacts
	rm -fr dist/
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	$(FIND_NAME) '*.pyc' -exec rm -f {} +
	$(FIND_NAME) '__pycache__' -exec rm -fr {} +


cov: sync ## check code coverage quickly with the default Python
	$(COVERAGE) run --source pycmd2 -m pytest
	$(COVERAGE) report -m
	$(COVERAGE) html
	$(BROWSER) htmlcov/index.html

doc: sync ## generate Sphinx HTML documentation, including API docs
	rm -f docs/pycmd2*.rst
	rm -f docs/modules.rst
	rm -rf docs/_build
	$(SPHINX_APIDOC) -o docs/ src/pycmd2
	$(SPHINX_BUILD) docs docs/_build
	sphinx-autobuild ./docs ./docs/_build/html --watch . --open-browser

dist: clean ## builds source and wheel package
	hatch build
	ls -l dist

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

init: clean sync ## initialize environment
	git init
	uvx pre-commit install

lint: sync ## check style with ruff
	$(RUFF) check src tests --fix

pub: dist ## publish to pypi
	hatch publish

sync: ## sync project using uv
	uv sync

test: sync ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

