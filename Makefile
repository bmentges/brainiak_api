CWD="`pwd`"
HOME_BRAINIAK ?= $(CWD)
BRAINIAK_CODE=$(HOME_BRAINIAK)/src
NEW_PYTHONPATH=$(BRAINIAK_CODE):$(PYTHONPATH)

clean:
	@find . -name "*.pyc" -delete

install:
	@echo "Installing dependencies..."
	@pip install -r $(HOME_BRAINIAK)/requirements.txt
	@pip install -r $(HOME_BRAINIAK)/requirements_test.txt
	@echo "Installing git hook"
	@cp ./tools/git-hooks/pre-commit ./.git/hooks/pre-commit
	@chmod ug+x ./.git/hooks/pre-commit

test: clean pep8 pep8_tests
	@echo "Running all tests..."
	@nosetests -s  --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests --with-xunit

unit: clean
	@echo "Running unit tests..."
	@nosetests -s --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests/unit --with-xunit

integration: clean
	@echo "Running integration tests..."
	@nosetests -x -s --with-coverage --cover-inclusive --cover-package=brainiak --tests=$(HOME_BRAINIAK)/tests/integration --with-xunit

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 $(HOME_BRAINIAK)/src/brainiak --ignore=E501,E126,E127,E128

pep8_tests:
	@echo "Checking tests code PEP8 compliance"
	@-pep8 $(HOME_BRAINIAK)/tests --ignore=E501,E126,E127,E128

run:
	@echo "Brainiak is alive!"
	PYTHONPATH="$(NEW_PYTHONPATH)" python -m brainiak.server

gunicorn:
	@echo "Running with gunicorn..."
	@pip install gunicorn
	cd $(BRAINIAK_CODE); PYTHONPATH="$(NEW_PYTHONPATH)" gunicorn -k egg:gunicorn#tornado brainiak.server:application -w 1

docs:
	@echo "Compiling and opening documentation..."
	@cd $(HOME_BRAINIAK)/docs; make run

console:
	@echo "Console Python inside Brainiak code (you must be on the correct Virtualenv)"
	@cd $(BRAINIAK_CODE); python
