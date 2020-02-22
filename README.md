# Sputnik API

Sample AWS API gateway and automated deployment pipeline.

## API
API Gateway with 2 endpoints

* GET ~/dev||prod/launch returns all launches 
* GET ~/dev||prod/launch?landed=1 returns all launches that have landed successfully

and 2 environments/stages
* https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev
* https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod


### Example GET URL
```bash
https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/launch
```

## DB Migration Script
A Python script is provided in the `scripts` that will load inital JSON data into a DynamoDB table.

```bash
python3 db_loader.py --src seed-data.json --table myDynamoDBTableName
```

## Environments
* ~~`dev` - development environment deployed from code stored in the `dev` branch of the GitHub repo~~
* `prod` - production environment deployed from code stored in the `master` branch of the GitHub repo


## CI/CD

The API for both environments is deployed automatically upon a code merge to the `dev` or `master` branch
for the `dev` and `prod` environments respectively.

The deployment pipelines are handled by AWS CodePipeline while the code is validated, tested, built and deployed
via AWS CodeBuild and SAM.


## Templates

### template.yaml
A SAM CloudFormation template that defines the related Lambda Function, DynamoDB table, API Gateway and IAM roles.

### pipeline.yaml
A CloudFormation template that defines the deployment pipeline (CodePipeline & CodeBuild project) and related resources.

#### Deployment example

```bash
aws cloudformation create-stack \
--profile sputnik \
--region us-east-1 \
--capabilities CAPABILITY_IAM \
--stack-name prod-sputnik-api-pipeline \
--template-body file://pipeline.yaml \
--parameters ParameterKey=GitHubRepo,ParameterValue=sputnik-api  \
ParameterKey=GitHubBranch,ParameterValue=prod  \
ParameterKey=GitHubOwner,ParameterValue=josh-butler  \
ParameterKey=GitHubToken,ParameterValue=[TOKEN-HERE]  \
ParameterKey=SamStackName,ParameterValue=prod-sputnik-api  \
ParameterKey=Environment,ParameterValue=prod
```


## Makefile
A Makefile is provided in the project root directory and is used to run commands during local development and deployment.

Default environment variables used by the Makefile can be overwritten by creating a `Makefile.env` file as shown below.

```bash
REGION=us-east-1
AWS_PROFILE=default
SAM_ARTIFACT_BUCKET=my-artifact-bucket
DEPLOY_ENV=prod
SAM_STACK_NAME=prod-sputnik-api
...
```

## Local Requirements
* Python 3
* Docker
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* `cicd.txt` defines Python dependencies only necesarry for local development and pre deployment testing.
  App specific dependencies are defined in `src/requirements.txt`


## Local development 

### Initial Local Setup
* Within the project root directory, create a Python venv by running: `make venv`
* Activate the venv with: `source venv/bin/activate`

### Testing
* Start the API locally with: `make api` or simply `make`
* Run `make test` to:
    * Run unit tests with Pytest
    * View current code coverage report
    * Validate code linting with Pylint

### Linting
* Code linting can be run in isolation with `make pylint`
* Pylint rules can be updated in the `.pylintrc` file


## Deploying
* ~~Deploy to `dev` by merging code into the `dev` repo branch~~
* Deploy to `prod` by merging code into the `master` repo branch 

Deployment state and logs can be viewed in the CodePipeline AWS web console.

### Pipelines
* ~~dev-sputnik-api-pipeline-CFPipeline-x~~
* prod-sputnik-api-pipeline-CFPipeline-x
