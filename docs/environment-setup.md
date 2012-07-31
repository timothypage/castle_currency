#Django Environment
How to setup the working environment for Django development.

####Clone the Git project and `cd` into its directory.
####Setup the virtual environment.
    virtualenv env-project-name

* The `no-site-packages` flag is unnecessary in the latest versions of Ubuntu.
* The .gitignore already contains an ignore statement for /env*. The environment will be ignored if the env- naming convention is followed and is in the project root.

####Activate the virtual environment.
    source env-project-name/bin/activate

####Install the dependencies.
    pip install -r DEPENDENCIES