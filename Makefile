NEW_PYTHONPATH="`pwd`/src:$(PYTHONPATH)"

clean:
	@find . -name "*.pyc" -delete

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@pip install -r requirements_test.txt

test: clean pep8 pep8_tests
	@echo "Running all tests..."
	@nosetests -s --with-coverage --cover-inclusive --cover-package=brainiak --tests=tests --with-xunit

unit: clean
	@echo "Running unit tests..."
	@nosetests -s --with-coverage --cover-inclusive --cover-package=brainiak --tests=tests/unit --with-xunit

functional: clean
	@echo "Running functional tests..."
	@nosetests -s --with-coverage --cover-inclusive --cover-package=brainiak --tests=tests/functional --with-xunit

integration: clean
	@echo "Running integration tests..."
	@nosetests -s --with-coverage --cover-inclusive --cover-package=brainiak --tests=tests/integration --with-xunit

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 src/brainiak --ignore=E501,E126,E127,E128

pep8_tests:
	@echo "Checking tests code PEP8 compliance"
	@-pep8 tests --ignore=E501,E126,E127,E128

run:
	@echo "Raising Brainiak..."
	@echo "TODO"
	#PYTHONPATH="$(NEW_PYTHONPATH)" python -m brainiak.server
