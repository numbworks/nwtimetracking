# SETTINGS
.PHONY: clear makefile-info type-concise changelog-concise setup-concise coverage-concise tryinstall-concise compile-concise compilenotebook-concise unittest-concise codemetrics-concise all-concise 
SHELL := /bin/bash
ROOT_DIR := $(shell cd .. && pwd)
MODULE_NAME = "nwtimetracking"
MODULE_VERSION = "5.0.1"
COVERAGE_THRESHOLD = 70

# TARGETS (VERBOSE)
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
	coverage html --include=$(MODULE_NAME).py && sed -n '/<table class="index" data-sortable>/,/<\/table>/p' htmlcov/class_index.html | pandoc --from html --to plain; \
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
	python -m venv venv; \
	source venv/bin/activate; \
	pip install dist/$(MODULE_NAME)*.whl; \
	pip show $(MODULE_NAME) | grep Version; \
	deactivate; \
	rm -rf build; \
	rm -rf dist; \
	rm -rf $(MODULE_NAME).egg-info; \
	rm -rf venv;
compile-verbose:
	@clear; \
	python -m py_compile $(ROOT_DIR)/src/$(MODULE_NAME).py;
compilenotebook-verbose:
	@clear; \
	jupyter nbconvert --to script $(ROOT_DIR)/src/$(MODULE_NAME).ipynb --output /home/nbconvert; \
	python -m py_compile /home/nbconvert.py; \
	rm /home/nbconvert.py;
unittest-verbose:
	@clear; \
	python $(ROOT_DIR)/tests/$(MODULE_NAME)tests.py;
codemetrics-verbose:
	@clear; \
	radon cc -a -s $(ROOT_DIR)/src/$(MODULE_NAME)*.py | grep -e '^[ ]*[CFM].*' | grep -v ' - A';
commitavg-verbose:
	@clear; \
	python $(ROOT_DIR)/scripts/commitavgcalculator.py;
check-pythonversion:
	@clear; \
	code="from nwpackageversions import LanguageChecker; print(LanguageChecker().get_version_status(required=(3, 12, 5)))"; \
	python -c "$$code"
check-requirements:
	@clear; \
	file_path="$(ROOT_DIR)/.devcontainer/Dockerfile"; \
	code="from nwpackageversions import RequirementChecker; print(RequirementChecker().try_check(file_path = '$$file_path', only_stable_releases = True, sort_requirement_details = True))"; \
	python -c "$$code";
update-codecoverage:
	@clear; \
	cd $(ROOT_DIR)/tests/; \
	coverage run -m unittest $(MODULE_NAME)tests.py > /dev/null 2>&1; \
	value=$$(coverage report --include=$(MODULE_NAME).py | grep -oP 'TOTAL\s+\d+\s+\d+\s+\K\d+(?=%)'); \
	if [ $$value -le 39 ]; then color="red"; elif [ $$value -le 69 ]; then color="orange"; else color="green"; fi; \
	url="https://img.shields.io/badge/coverage-$${value}.0%25-$${color}"; \
	echo "$$url" > $(ROOT_DIR)/codecoverage.txt; \
	curl -s $$url -o $(ROOT_DIR)/codecoverage.svg; \
	if [ $$? -eq 0 ]; then echo "[OK] $@: coverage badge updated successfully!"; else echo "[ERROR] $@: failed to update coverage badge."; fi;

# TARGETS (CONCISE)
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
	value=$$(coverage report --include=$(MODULE_NAME).py | grep -oP 'TOTAL\s+\d+\s+\d+\s+\K\d+(?=%)'); \
	if [ $$value -ge $(COVERAGE_THRESHOLD) ]; then echo "[OK] $@: unit test coverage >= $(COVERAGE_THRESHOLD)%."; else echo "[WARNING] $@: unit test coverage < $(COVERAGE_THRESHOLD)%."; fi;
tryinstall-concise:
	@value=$$(make tryinstall-verbose 2>&1); \
	last_chars=$$(echo "$$value" | tail -c 100); \
	if [[ "$$last_chars" == *"Version: $(MODULE_VERSION)"* ]]; then echo "[OK] $@: installation process works."; else echo "[WARNING] $@: installation process fails!"; fi;
compile-concise:
	@value=$$(python -m py_compile $(ROOT_DIR)/src/$(MODULE_NAME).py 2>&1); \
	if [ -z "$${value}" ]; then value=0; else value=1; fi; \
	if [ $$value -eq 0 ]; then echo "[OK] $@: compiling the library throws no issues."; else echo "[WARNING] $@: compiling the library throws some issues."; fi;
compilenotebook-concise:
	@jupyter nbconvert --to script $(ROOT_DIR)/src/$(MODULE_NAME).ipynb --output /home/nbconvert > /dev/null 2>&1; \
	value=$$(python -m py_compile /home/nbconvert.py 2>&1); \
	rm /home/nbconvert.py; \
	if [ -z "$${value}" ]; then value=0; else value=1; fi; \
	if [ $$value -eq 0 ]; then echo "[OK] $@: compiling the notebook throws no issues."; else echo "[WARNING] $@: compiling the notebook throws some issues."; fi;
unittest-concise:
	@value=$$(python $(ROOT_DIR)/tests/$(MODULE_NAME)tests.py 2>&1 | grep -oP '(?<=Ran )\d+(?= tests)'); \
	if [ -z "$${value}" ]; then value=0; fi; \
	if [ $$value -gt 0 ]; then echo "[OK] $@: '$$value' tests found and run."; else echo "[WARNING] $@: '$$value' tests found and run."; fi;
codemetrics-concise:
	@value=$$(radon cc -a -s $(ROOT_DIR)/src/$(MODULE_NAME)*.py  | grep -oP "Average complexity: \K[A-F]"); \
	if [[ "$$value" == *"A"* ]]; then echo "[OK] $@: the cyclomatic complexity is excellent ('$$value')."; else echo "[WARNING] $@: the cyclomatic complexity is not excellent ('$$value')"; fi;

# TARGETS (UTILITY)
classdiagram-basic:
	@clear; \
	pyreverse $(ROOT_DIR)/src/$(MODULE_NAME).py -o mmd -d /home/$(MODULE_NAME)/; \
	md_file="/home/$(MODULE_NAME)/classes.mmd"; \
	tmp_file="/home/$(MODULE_NAME)/temp.mmd"; \
	final_file="/home/$(MODULE_NAME)/Diagram-Architecture.md"; \
	awk '/classDiagram|--\*/ { print }' $$md_file > $$tmp_file; \
	echo '```mermaid' > $$md_file; \
	cat $$tmp_file >> $$md_file; \
	echo '```' >> $$md_file; \
	rm $$tmp_file; \
	mv $$md_file $$final_file

# TARGETS (AGGREGATE)
all-concise: clear makefile-info type-concise changelog-concise setup-concise coverage-concise compile-concise compilenotebook-concise unittest-concise codemetrics-concise tryinstall-concise