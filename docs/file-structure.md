#Django 1.4 File Structure

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
        static/ (*)
        templates/ (*)

* Note: Placing the "static" and "templates" directories in the root of the project makes it difficult to have static and template files in the re-usable sub-applications.


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

For re-usable applications, we need a good way to integrate static and template files.