CWD = `pwd`
HOME_BRAINIAK ?= $(CWD)
NEW_PYTHONPATH="$(HOME_BRAINIAK)/src:$(PYTHONPATH)"

clean:
	@find . -name "*.pyc" -delete

install:
	@echo "Installing dependencies..."
	@pip install -r $(HOME_BRAINIAK)/requirements.txt
	@pip install -r $(HOME_BRAINIAK)/requirements_test.txt
	@pip install -r $(HOME_BRAINIAK)/docs/requirements.txt

test: clean pep8 pep8_tests coverage
	@echo "Running all tests..."
	@nosetests -s  --tests=$(HOME_BRAINIAK)/tests --with-xunit

unit: clean
	@echo "Running unit tests..."
	@nosetests -s  --tests=$(HOME_BRAINIAK)/tests/unit --with-xunit

coverage: clean
	@nosetests -s --with-coverage --cover-inclusive --cover-package=brainiak

functional: clean
	@echo "Running functional tests..."
	@nosetests -s --tests=$(HOME_BRAINIAK)/tests/functional --with-xunit

integration: clean
	@echo "Running integration tests..."
	@nosetests -s  --tests=$(HOME_BRAINIAK)/tests/integration --with-xunit

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 $(HOME_BRAINIAK)/src/brainiak --ignore=E501,E126,E127,E128

pep8_tests:
	@echo "Checking tests code PEP8 compliance"
	@-pep8 $(HOME_BRAINIAK)/tests --ignore=E501,E126,E127,E128

run:
	@echo "Brainiak is alive!"
	PYTHONPATH="$(NEW_PYTHONPATH)" python -m brainiak.server

docs:
	@echo "Compiling and opening documentation..."
	@cd $(HOME_BRAINIAK)/docs; make run
