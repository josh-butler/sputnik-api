.PHONY: all \
api run \
sam-build sam-deploy sam-package \
install pre-build build post-build \
test test-unit \
venv

-include Makefile.env

REGION ?= us-east-1
AWS_OPTIONS=

ROOT_PATH=$(PWD)
SRC_PATH=$(ROOT_PATH)/src
BUILD_PATH=$(ROOT_PATH)/.aws-sam/build
TESTS_PATH=$(ROOT_PATH)/tests
BUILD_DOCS_PATH=build/docs

VENV_PATH=.venv
VENV_ACTIVATE_PATH=$(VENV_PATH)/bin/activate
SRC_REQUIREMENTS=$(SRC_PATH)/requirements.txt
CICD_REQUIREMENTS=cicd.txt

FIND_ALL_SRC=find $(SRC_PATH) -name "*.py"
COVERAGE_MIN ?= 10

PYLINT=pylint
PYLINT_OPTIONS=
REPORT_PYLINT=$(BUILD_DOCS_PATH)/pylint.log

ifdef AWS_PROFILE
AWS_OPTIONS=--profile $(AWS_PROFILE)
endif

DEPLOY_PARAMS=--parameter-overrides "Environment=$(DEPLOY_ENV)"
# ifdef ENVIRONMENT_TYPE
# DEPLOY_PARAMS += "EnvType=$(ENVIRONMENT_TYPE)"
# endif

all: api

clean:
	# rm -rf $(VENV_PATH)
	find . -iname "*.pyc" -delete
	rm -rf $(BUILD_PATH)
	rm -f .coverage

venv: $(VENV_ACTIVATE_PATH)

$(VENV_ACTIVATE_PATH): $(CICD_REQUIREMENTS) $(SRC_REQUIREMENTS)
	test -d $(VENV_PATH) || python3 -m venv $(VENV_PATH)
	. $(VENV_ACTIVATE_PATH); pip install --upgrade pip; pip install -Ur $(CICD_REQUIREMENTS) -Ur $(SRC_REQUIREMENTS)
	touch $(VENV_ACTIVATE_PATH)

api:
	# sam build --use-container
	sam build
	sam local start-api

run:
	sam local invoke $(LAMBDA_NAME) -e event.json --env-vars env.json $(AWS_OPTIONS)

sam-build:
	sam build

sam-package:
	cd $(BUILD_PATH) && sam package \
	--template-file template.yaml \
	--s3-bucket $(SAM_ARTIFACT_BUCKET) \
	--output-template-file packaged.yaml \
	$(AWS_OPTIONS)

sam-deploy: 
	cd $(BUILD_PATH) && sam deploy \
	--template-file packaged.yaml \
	--stack-name $(SAM_STACK_NAME) \
	--capabilities CAPABILITY_NAMED_IAM \
	$(DEPLOY_PARAMS) $(AWS_OPTIONS)

test: pylint test-unit
	
test-unit:
	@if [ -d $(TESTS_PATH)/unit ]; then \
		export PYTHONPATH=$(SRC_PATH); \
		pytest \
		--cov=$(SRC_PATH) \
		--cov-report term-missing \
		--cov-fail-under=$(COVERAGE_MIN) $(TESTS_PATH) \
		|| (echo "Unit tests failed!"; exit 1) \
	fi

pylint:
	@if [ -d $(SRC_PATH) ]; then \
		mkdir -p $(BUILD_DOCS_PATH); \
		export PYTHONPATH=$(SRC_PATH); \
		test -e $(PWD)/.pylintrc || $(PYLINT) --generate-rcfile > $(PWD)/.pylintrc; \
		$(FIND_ALL_SRC) | xargs $(PYLINT) $(PYLINT_OPTIONS) > $(REPORT_PYLINT) || (cat $(REPORT_PYLINT); exit 1); \
	fi

install:
	apt-get update -y
	pip install --upgrade pip
	pip install aws-sam-cli
	pip install -Ur $(CICD_REQUIREMENTS) -Ur $(SRC_REQUIREMENTS)

pre-build: test

build: sam-build sam-package

post-build: sam-deploy
