#Django Environment
How to setup the working environment for Django development.

####Clone the Git project and `cd` into its directory.
####Setup the virtual environment.
    virtualenv env-project-name

* The `no-site-packages` flag is unnecessary in the latest versions of Ubuntu.
* The .gitignore already contains an ignore statement for `/env*`. The environment will be ignored if the env- naming convention is followed and under the project root.

####Activate the virtual environment.
    source env-project-name/bin/activate

####Install the dependencies.
    pip install -r DEPENDENCIES

If the virtual environment has been activated and its dependencies installed, you should be able to run the django project's test suite.

	python manage.py test

To run the server, the database must be sync'd.

    python manage.py syncdb

And then the server can be run (defaults to localhost:8000).

    python manage.py runserver