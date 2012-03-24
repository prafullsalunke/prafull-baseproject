All configuration files for the servers are kept inside confs folder.
Run the file requirements.sh inside conf to install system dependencies

To run the project on development.

$ cd base

$ python manage.py runserver

To run the project on production.

./server.sh start|stop

The server runs on single threaded twisted framework.

Directory Structure:

- confs   :   All server confs and system package install scripts

- base    :   The basic project template created by django-admin

- dump    :   Data dumps to run a project. init.sql should have the latest dump. 
              state_city.sql has a dump for Indian state and cities
- libs    :   All python external libraries and applications

- static  :   All static data to be kept here, nginx can serve these directly

- uploads :   All uploads using django forms

- twisted__server : Twisted server code


Libraries included:

- customdb : Direct db query scripts

- customforms : Library to do ajax and form handling using urls

- south  :  Database migration package

- xl2python : package to make excel/csv uploads easy in python

- xlrd & xlwt  : excel reading packages

