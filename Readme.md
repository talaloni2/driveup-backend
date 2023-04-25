#DriveUp Backend
Python Version: 3.10.6
This repo is the backend for the DriveUp app(for both drivers and riders)<br>

##Running tests
<b>Make sure docker is installed on your computer<br></b>
First run these 2 commands:<br>
* <code>docker run --rm --name postgres-db -e POSTGRES_PASSWORD=<your-pass> -p 5432:5432 -d postgres:13</code><br>

execute the following command(while on the repo dir):<br>
<code>pytest</code>
* Make sure the following variables are used in the shell(or configure it in pycharm test configuration)
  * DB_USER=postgres
  * DB_PASS=<your-pass>
  * DB_HOST=localhost
  * DB_PORT=5432

##Running the app
<b>Make sure docker is installed on your computer<br></b>
First run these 2 commands:<br>
* <code>docker run --rm --name postgres-db -e POSTGRES_PASSWORD=<your-pass> -p 5432:5432 -d postgres:13</code><br>

* Make sure the following variables are used in the shell(or configure it in pycharm test configuration)
  * DB_USER=postgres
  * DB_PASS=<your-pass>
  * DB_HOST=localhost
  * DB_PORT=5432

Execute the following command from project root dir:<br>
python -m main

##Running with docker
Make sure you have docker installed
* clone the subscription handler repository: <url>https://github.com/avivaloni10/subscriptions_handler</url>
* <code>cd</code> into the cloned directory.
* execute <code>docker build -t driveup-subscription-handler:0.0.1 .</code>
* clone the users handler repository: <url>https://github.com/avivaloni10/users_hundler</url>
* <code>cd</code> into the cloned directory.
* execute <code>docker build -t driveup-user-handler:0.0.1 .</code>
* clone the knapsack solver repository: <url>https://github.com/avivaloni10/subscriptions_handler</url>
* <code>cd</code> into the knapsack-solver project directory.
* execute <code>docker build -t knapsack-engine:0.0.1 .</code>
* execute <code>docker-compose up -d</code>
  * If you wish to stop the dockers, execute: <code>docker-compose down</code>