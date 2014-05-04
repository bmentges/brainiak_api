CWD="`pwd`"
HOME_BRAINIAK ?= $(CWD)
BRAINIAK_CODE=$(HOME_BRAINIAK)/src
NEW_PYTHONPATH=$(BRAINIAK_CODE):$(PYTHONPATH)
EXTRA_NOSE_PARAMS ?= $(NOSE_PARAMS)

.PHONY: docs

clean:
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete

clean_redis:
	@redis-cli FLUSHDB

install:
	@echo "Installing dependencies..."
	@pip install -r $(HOME_BRAINIAK)/requirements.txt
	@pip install -r $(HOME_BRAINIAK)/requirements_test.txt
	@echo "Installing git hook"
	@cp ./tools/git-hooks/pre-commit ./.git/hooks/pre-commit
	@chmod ug+x ./.git/hooks/pre-commit

tests: clean pep8 pep8_tests
	@echo "Running pep8, unit and integration tests..."
	@nosetests -s  --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests  --exclude-dir=$(HOME_BRAINIAK)/tests/acceptance --exclude=$(HOME_BRAINIAK)/tests/acceptance --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS) --with-stopwatch

unit: clean
	@echo "Running unit tests..."
	@nosetests -s --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests/unit --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS) --with-stopwatch --stopwatch-file=.nose-stopwatch-times-unit

integration: clean
	@echo "Running integration tests..."
	@nosetests -s --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests/integration --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS) --with-stopwatch --stopwatch-file=.nose-stopwatch-times-integration

acceptance: clean
	@echo "Running acceptance tests..."
	@nosetests -s  --tests=$(HOME_BRAINIAK)/tests/acceptance --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS)

acceptance_cma: clean
	@echo "Running acceptance tests for the CMAaaS..."
	@nosetests -s -x --tests=$(HOME_BRAINIAK)/tests/acceptance/cma --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS)

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 $(HOME_BRAINIAK)/src/brainiak --ignore=E501,E126,E127,E128

pep8_tests:
	@echo "Checking tests code PEP8 compliance"
	@-pep8 $(HOME_BRAINIAK)/tests --ignore=E501,E126,E127,E128

release:
	@# Usage: make release type=major message="Integration to ActiveMQ" (other options: minor or micros)
	@echo "Tagging new release..."
	@git fetch --tags
	@cd src; python -c "from brainiak.utils.git import build_next_release_string; print build_next_release_string('$(type)')" > brainiak/version.py
	@cd src; git tag `python -c "from brainiak.utils.git import compute_next_git_tag; print compute_next_git_tag('$(type)')"` -m "$(message)"

run:
	@echo "Brainiak is alive!"
	PYTHONPATH="$(NEW_PYTHONPATH)" python -m brainiak.server

gunicorn:
	@echo "Running with gunicorn..."
	@pip install gunicorn
	PYTHONPATH="$(NEW_PYTHONPATH)" gunicorn -k egg:gunicorn#tornado brainiak.server:application -w 10

nginx:
	sudo nginx -c $(HOME_BRAINIAK)/config/local/nginx.conf # run on 0.0.0.0:80

test-nginx:
	sudo nginx -t -c $(HOME_BRAINIAK)/config/local/nginx.conf

supervisor:
	PYTHONPATH="$(NEW_PYTHONPATH)" supervisord -c config/local/supervisord.conf -n -edebug

docs: clean
	@echo "Compiling and opening documentation..."
	@cd $(HOME_BRAINIAK)/docs; make html

console:
	@echo "Console Python inside Brainiak code (you must be on the correct Virtualenv)"
	@PYTHONPATH="$(BRAINIAK_CODE):$(NEW_PYTHONPATH)" python


# i18n #0
# If "string" should be translated, wrap it using _("string")

# i18n #1
# Create Brainiak translation template (POT) at locale/brainiak.pot, based on strings wrapped using _()
# Note: run whenever new strings wrapped using _() are added to Brainiak
translate_template:
	@xgettext --language=Python --keyword=_ --directory=src --output=locale/brainiak.pot --from-code=UTF-8 `cd src; find . -name "*.py"`

# i18n #2
# Merge translation template (POT) definitions to existing Portuguese translation file (PO)
portuguese_dictionary: translate_template
	@msgmerge --update --backup=off locale/pt_BR/LC_MESSAGES/brainiak.po locale/brainiak.pot

# i18n #3
# Translate whatever needs to be translated at brainiak.po file

# i18n #4
# Compile Portuguese translation file (PO) into a .MO file, which is used by Brainiak
# This final .MO file is used by Tornado
compile_portuguese:
	@cd locale/pt_BR/LC_MESSAGES; msgfmt brainiak.po -o brainiak.mo
