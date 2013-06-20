CWD="`pwd`"
HOME_BRAINIAK ?= $(CWD)
BRAINIAK_CODE=$(HOME_BRAINIAK)/src
NEW_PYTHONPATH=$(BRAINIAK_CODE):$(PYTHONPATH)
EXTRA_NOSE_PARAMS ?= $(NOSE_PARAMS)

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

test: clean pep8 pep8_tests
	@echo "Running pep8, unit and integration tests..."
	@nosetests -s  --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests  --exclude-dir=$(HOME_BRAINIAK)/tests/acceptance --exclude=$(HOME_BRAINIAK)/tests/acceptance --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS)

unit: clean
	@echo "Running unit tests..."
	@nosetests -s --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests/unit --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS)

integration: clean
	@echo "Running integration tests..."
	@nosetests -s --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests/integration --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS)

acceptance: clean
	@echo "Running acceptance tests..."
	@nosetests -s  --tests=$(HOME_BRAINIAK)/tests/acceptance --with-xunit --with-spec --spec-color $(EXTRA_NOSE_PARAMS)

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
	@cd $(BRAINIAK_CODE); python -c "from brainiak.utils.git import build_next_release_string; print build_next_release_string()" > brainiak/version.py
	@cd $(BRAINIAK_CODE); git tag `python -c "from brainiak.utils.git import compute_next_git_tag; print compute_next_git_tag('$(type)')"` -m "$(message)"

run:
	@echo "Brainiak is alive!"
	PYTHONPATH="$(NEW_PYTHONPATH)" python -m brainiak.server

gunicorn:
	@echo "Running with gunicorn..."
	@pip install gunicorn
	cd $(BRAINIAK_CODE); PYTHONPATH="$(NEW_PYTHONPATH)" gunicorn -k egg:gunicorn#tornado brainiak.server:application -w 10

nginx:
	sudo nginx -c $(HOME_BRAINIAK)/config/local/nginx.conf # run on 0.0.0.0:80

test-nginx:
	sudo nginx -t -c $(HOME_BRAINIAK)/config/local/nginx.conf

supervisor:
	PYTHONPATH="$(NEW_PYTHONPATH)" supervisord -c config/local/supervisord.conf -n -edebug

docs:
	@echo "Compiling and opening documentation..."
	@cd $(HOME_BRAINIAK)/docs; make run

console:
	@echo "Console Python inside Brainiak code (you must be on the correct Virtualenv)"
	@cd $(BRAINIAK_CODE); python
