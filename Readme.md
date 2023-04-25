# DriveUp Backend
Python Version: 3.10.6
This repo is the backend for the DriveUp app(for both drivers and riders)

## Running tests
Make sure docker is installed on your computer
First run these 2 commands:
* `docker run --rm --name postgres-db -e POSTGRES_PASSWORD=<your-pass> -p 5432:5432 -d postgres:13`

execute the following command(while on the repo dir):
`pytest`
* Make sure the following variables are used in the shell(or configure it in pycharm test configuration)
  * DB_USER=postgres
  * DB_PASS=<your-pass>
  * DB_HOST=localhost
  * DB_PORT=5432

## Running with docker
* Make sure you have docker installed
* `cd` into project directory
* Execute `docker-compose up -d`
* To shut down docker-compose, execute `docker-compose down`
  * To shut down docker-compose AND remove database data, execute `docker-compose down --volumes`

## Running the app
* Execute the steps of [Running with docker](#Running with docker)
* Wait fot ~20 seconds for docker-compose to stabilize (In the meantime do the next step)
* Set shell variables (or update Pycharm's environment variables under run configurations) as below:
`DB_HOST=localhost`
`DB_PASS=postgres`
`DB_PORT=5433`
`DB_USER=postgres`
`GEOCODING_API_KEY=<GET_API_KEY_FROM_TEAM_MEMBER>`
`KNAPSACK_SERVICE_URL=http://localhost:8003`
`PYTHONUNBUFFERED=1`
`SERVER_PORT=8005`
`SUBSCRIPTIONS_HANDLER_BASE_URL=http://localhost:8001`
`USERS_HANDLER_BASE_URL=http://localhost:8000`
* Execute `python -m main`

## How to update the docker image after code is completed?
* Check out the last published version in [here](<url>https://hub.docker.com/repository/docker/talaloni19920/driveup-backend/tags?page=1&ordering=last_updated</url>)
* Make sure you are a collaborator in this docker repository
* If this is your first time doing this, execute the following commands:
  * `docker buildx install`
  * `docker buildx create --name mybuilder --platform linux/amd64,linux/arm64`
  * `docker buildx use mybuilder`
* Now, build the image and push it using docker's buildx:
  * `docker buildx build --platform linux/amd64,linux/arm64 -t talaloni19920/driveup-backend:<LAST_IMAGE_TAG_PLUS_ONE_IN_LAST_NUMBER> talaloni19920/driveup-backend:latest . --push`
* After image is pushed, execute the following:
  * `docker-compose down`
  * `docker-compose pull`
  * `docker-compose up -d`