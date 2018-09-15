.. _ci:

Continuous Integration
========================

Nitpicker has a special command to run on the side of the CI server:

::

    python -m nitpicker check --all-runs-passed --has-new-runs

Flag *--all-runs-passed* provides a check if all the last run reports of the project have only
passed tests. If the check failed the program exists with error 1.

Flag *--has-new-runs* provides a check if the current branch has some new runs comparing
the main branch (*master* by default).  If the check failed the program exists with error 1.