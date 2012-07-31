#Django Environment

1. Clone the Git project and `cd` into its directory.
2. Setup the virtual environment.

    virtualenv env-project-name

	* The `no-site-packages` flag is unnecessary in the latest versions of Ubuntu.
	* The .gitignore already contains an ignore statement for env*. If the env- naming convention is followed it should be ignored automatically.

3. Activate the virtual environment.

    source env-project-name/bin/activate

4. Install the dependcies.

    pip install -r DEPENDENCIES