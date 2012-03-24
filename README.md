All configuration files for the servers are kept inside confs folder.
Run the file requirements.sh inside conf to install system dependencies

To run the project on development.

$ cd base
$ python manage.py runserver

To run the project on production.

./server.sh start|stop

The server runs on single threaded twisted framework.

Basic django project with following libraries
