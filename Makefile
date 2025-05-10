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

BROWSER := python -c "$$BROWSER_PYSCRIPT"
COVERAGE := coverage
RUFF := uvx ruff
UPDATE_BUILD_DATE := python -c "$$UPDATE_BUILDDATE_SCRIPT"
SPHINX_APIDOC := sphinx-apidoc
SPHINX_BUILD := sphinx-build

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
