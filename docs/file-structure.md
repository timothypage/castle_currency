#Django 1.4 File Structure

Example file structure for the main Django project, applications, and files.

###Projects

    project/
        project sub-directory/
            project sub-application/
            project sub-application/
            settings.py
            wsgi.py
            urls.py
        re-usable sub-application/
        re-usable sub-application/
        static/ (∗)
        templates/ (∗)

∗ Note: Placing the "static" and "templates" directories in the root of the project makes it difficult to have static and template files in the re-usable sub-applications.


###Applications

    application/
        models.py (there must be a models.py file for the app to be recognized)
        views.py
        urls.py
        admin.py
        tests/
            __init__.py (tests from the other files must be imported here)
            models.py
            views.py
        management/
            __init__.py
            commands/
                __init__.py
                management-job.py

Tests are broken into a separate sub-directory. The filename of the test corresponds to the file it is testing.

For re-usable applications, we need a good way to integrate static and template files.


###Files

Any Python code files should begin with the UTF-8 magic mark.

    # -*- coding: utf-8 -*

Any import statements should follow. These should be sorted alphabetically. I also separate them into standard library imports, third-party imports, and local application imports.

    import datetime

    from django.conf import settings
    from django.db import connection
    from django.shortcuts import render

    from panopticon.models import PageView

Function names should immediately be followed by a comment.

    def add_masquerade_to_url(url, user_id):
        """
        Adds the masquerade GET variable to the requested url
        """
        pass

Code should follow the official [Python style guide (PEP8)](http://www.python.org/dev/peps/pep-0008/).