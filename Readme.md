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
