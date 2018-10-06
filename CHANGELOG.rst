Release 0.4.0
---------------------------------
* Add flag --only for 'run' command (@flipback)
* Add command 'validate' to check format of all the test on QA directory (@flipback)
* #11 Fix validation error in command list (@flipback)
* Nitpicker can be run as a command (`nitpicker` instead of `python -m nitpicker) (@flipback)

Release 0.3.0
---------------------------------
* #3 Command 'check --all-runs-passed' checks if all of the last runs are passed (@flipback)
* #3 Command 'check --has-new-runs' checks if there are some new runs in the feature branch (@flipback)

Release 0.2.0
---------------------------------
* #6 Fix output of command 'list' (@flipback)
* #2 Command 'add' gets user name and email from Git repo (@flipback)
* #8 Fix error of utf-8 encoding in command 'add' (@Rumpelshtinskiy)
* Make format of test cases more friendly (@flipback):

.. code-block:: yaml

    description: Some test to test something
    author:
    email:
    tags:
    setup:
        - Do something
    teardown:
        - Do something
    steps:
        - Some action => Some expectation
        - Some action => Some expectation

Release 0.1.4
---------------------------------
* Fix UTF-8 bug in YAML dumping (@flipback)

Release 0.1.3
---------------------------------
* Fix PyPi distribution

Release 0.1.0
---------------------------------
* #1 Report generation about test runs in MD format (@flipback)
* #7 A user can comment the failed step (@flipback)
* #5 A user can edit a new test case in editor at once after creation (@flipback)

Release 0.0.3
---------------------------------
* Fix input on Windows (@flipback)
* Fix saving a report at the end of command *add* (@flipback)
