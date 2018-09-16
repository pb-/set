all: lint test
.PHONY: all

lint:
	pipenv run flake8 set
.PHONY: lint

test:
	pipenv run pytest -v set
.PHONY: test

test_cov:
	pipenv run pytest -v --cov . --cov-report term-missing set
.PHONY: test

dev_install:
	pipenv install --dev
.PHONY:
