.. _settings:

Settings
========================

You can customize your work with Nitpicker by using configuration file *.nitpicker* in
the root directory of your project. The configuration file is written in YAML format and has
the following options:

* **qa_dir** - the relative path of QA directory inside the project (default: 'qa')
* **no_editor** - if set in *true*, a new test is not opened in a text editor after command 'add' (default: false)
* **cvs** - the type of CVS, currently only git is supported (default: 'git')
* **main_branch** - the main branch, where all new feature branch are to merge (default: 'master'). See :ref:`ci` for more information.

A setting file's example:

.. code-block:: yaml

    qa_dir: some_other_dir
    no_editor: true
    main_branch: develop