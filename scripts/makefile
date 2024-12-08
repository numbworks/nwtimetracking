# SETTINGS
.PHONY: clear makefile-info type-concise changelog-concise setup-concise coverage-concise tryinstall-concise all-concise 
SHELL := /bin/bash
ROOT_DIR := $(shell cd .. && pwd)
MODULE_NAME = "nwtimetracking"
MODULE_VERSION = "4.0.0"
COVERAGE_THRESHOLD = 70

# TARGETS
clear:
	@clear
makefile-info:
	@echo "MODULE_NAME: $(MODULE_NAME)"; \
	echo "MODULE_VERSION: $(MODULE_VERSION)"; \
	echo "COVERAGE_THRESHOLD: $(COVERAGE_THRESHOLD)%"

type-verbose:
	@clear; \
	mypy $(ROOT_DIR)/src/$(MODULE_NAME).py --check-untyped-defs --disable-error-code=import-untyped; \
	mypy $(ROOT_DIR)/tests/$(MODULE_NAME)tests.py --check-untyped-defs --disable-error-code=import-untyped --disable-error-code=import-not-found;
coverage-verbose:
	@clear; \
	cd $(ROOT_DIR)/tests/; \
	coverage run -m unittest $(MODULE_NAME)tests.py > /dev/null 2>&1; \
	rm -rf htmlcov; \
	coverage html --omit=$(MODULE_NAME)tests.py && sed -n '/<table class="index" data-sortable>/,/<\/table>/p' htmlcov/class_index.html | pandoc --from html --to plain; \
	sleep 3; \
	rm -rf htmlcov;
tryinstall-verbose:
	@clear; \
	cd /home; \
	rm -rf build; \
	rm -rf dist; \
	rm -rf $(MODULE_NAME).egg-info; \
	rm -rf venv; \
	python /workspaces/$(MODULE_NAME)/src/setup.py bdist_wheel; \
	python3 -m venv venv; \
	source venv/bin/activate; \
	pip install dist/$(MODULE_NAME)*.whl; \
	pip show $(MODULE_NAME) | grep Version; \
	deactivate; \
	rm -rf build; \
	rm -rf dist; \
	rm -rf $(MODULE_NAME).egg-info; \
	rm -rf venv;

type-concise:
	@value=$$(mypy $(ROOT_DIR)/src/$(MODULE_NAME).py --disable-error-code=import-untyped | grep -c "error:"); \
	value+=$$(mypy $(ROOT_DIR)/tests/$(MODULE_NAME)tests.py --disable-error-code=import-untyped  --disable-error-code=import-not-found | grep -c "error:"); \
	if [ $$value -eq 0 ]; then echo "[OK] $@: passed!"; else echo "[WARNING] $@: not passed! '$$value' error(s) found!"; fi;
changelog-concise:
	@value=$$(cat $(ROOT_DIR)/CHANGELOG | grep -c -e "v$(MODULE_VERSION)$$" -e "v$(MODULE_VERSION) - BREAKING CHANGES$$"); \
	if [ $$value -eq 1 ]; then echo "[OK] $@: 'CHANGELOG' updated to current version!"; else echo "[WARNING] $@: 'CHANGELOG' not updated to current version!"; fi;
setup-concise:
	@value=$$(cat $(ROOT_DIR)/src/setup.py | grep -oP 'MODULE_VERSION\s*:\s*str\s*=\s*"\K[\d.]+'); \
	if [ $$value == "$(MODULE_VERSION)" ]; then echo "[OK] $@: 'setup.py' updated to current version!"; else echo "[WARNING] $@: 'setup.py' not updated to current version!"; fi;
coverage-concise:
	@cd $(ROOT_DIR)/tests/; \
	coverage run -m unittest $(MODULE_NAME)tests.py > /dev/null 2>&1; \
	value=$$(coverage report --omit=$(MODULE_NAME)tests.py | grep -oP 'TOTAL\s+\d+\s+\d+\s+\K\d+(?=%)'); \
	if [ $$value -ge $(COVERAGE_THRESHOLD) ]; then echo "[OK] $@: unit test coverage >= $(COVERAGE_THRESHOLD)%."; else echo "[WARNING] $@: unit test coverage < $(COVERAGE_THRESHOLD)%."; fi;
tryinstall-concise:
	@value=$$(make tryinstall-verbose 2>&1); \
	last_chars=$$(echo "$$value" | tail -c 100); \
	if [[ "$$last_chars" == *"Version: $(MODULE_VERSION)"* ]]; then echo "[OK] $@: installation process works."; else echo "[WARNING] $@: installation process fails!"; fi;

# AGGREGATE TARGETS
all-concise: clear makefile-info type-concise changelog-concise setup-concise coverage-concise tryinstall-concise