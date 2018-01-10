.. _developer:

***************
Developer Guide
***************

This document outlines the process for creating new test modules and contributing back to the package.

Global test configuration
=========================

Configuration which applies to every test module is set in the ``caltest/conftest.py``.  For the purposes of adding new
tests the most import detail is that this is where the input for each step is set.  This is done in the
``pytest_generate_tests()`` function.

.. code-block:: python

    def pytest_generate_tests(metafunc):
        with open(metafunc.config.option.config) as config_file:
            config = json.load(config_file)
        steps = ['dq_init', 'saturation', 'superbias', 'linearity', 'dark_current',
                 'jump', 'ramp_fit']
        # parametrize tests with the input files supplied for that step
        for step in steps:
            if step in metafunc.module.__name__ and config.get(step):
                metafunc.parametrize("input_file", config[step], scope='module')

This function checks whether currently implemented ``steps`` are named in the input
JSON ``config`` file and matches the current module ``__name__``.  If an input file is supplied in the JSON file a
fixture_ is created named ``input_file`` to supply the path to the input file.

This file is path is in turn passed to another fixture ``fits_input``.  This fixture has ``scope='module'`` ensuring
that the input FITS file is opened only once per test module.  This fixture is created for every test module and provides
the starting point for testing.

Writing a new test module
=========================

New test modules should be written in a python file in ``caltest/test_<pipeline_stage>/test_<pipeline_step>.py``.  For
example, tests for the DQ Initialization step are in ``caltest/test_caldetector1/test_dq_init.py``.  In general, each
test module will require at least to functions.  A test which runs the relevant pipeline step and saves the output, and
a fixture open the output fits file and makes it available for subsequent tests.

The convention for naming the test which runs the test is ``test_<step_name>_step`` and the fixture is named
``fits_output``.  Using ``test_dq_init.py`` as an example, the first test defined in the module is

.. code-block:: python

    def test_dq_init_step(fits_input):
        """Make sure the DQInitStep runs without error."""
        DQInitStep.call(fits_input, save_results=True)

This test uses the ``fits_input`` fixture defined earlier in the ``conftest.py`` and runs the ``DQInitStep``.  Note that
the ``fits_output`` fixture is defined before the step in the file.  In pytest, tests are run in the order they appear
and fixtures are intialized the first time they are used.  ``test_dq_init_step`` is always run first and requires only the
``fits_input`` fixture to run, only when ``test_pixeldq_initialization`` is run subsequently is ``fits_output``
initialized ensuring that the output file has been created.  Thus, the ``test_<step_name>_step`` should always be the
first test defined the test module.

The ``fits_output`` fixture uses a ``yield`` to supply the FITS ``HDUList`` this allows for "clean up" to be done once
all tests requiring the fixture have been run.

.. code-block:: python

    @pytest.fixture(scope='module')
    def fits_output(fits_input):
        fname = '_dqinitstep.'.join(fits_input[0].header['filename'].split('.'))
        fname = fname.replace('_uncal', '')
        yield fits.open(fname)
        os.remove(fname)

In this context we us this to delete the output FITS file after we are done testing.


Making code contributions
=========================

Code contributions should be made through pull requests on GitHub_.  To get started, first fork the repository.  This
will create a copy of the repository for you to work on.  Then clone your repository to local machine.

.. code::

    git clone https://github.com/<your_github_username>/calibration-pipeline-testing-tool.git

Development should be done in a separate branch than ``master``.  Before beginning work on a new feature create a branch

.. code::

    cd calibration-pipeline-testing-tool
    git checkout -b new_feature

When you are ready to merge changes into the official repository open a Pull Request here_.  Choose your fork and branch
as the "head".  Then click "Create pull request".  Give a short and long description of the work done in the pull request
once it is reviewed it can be merged into the official repository.

.. _fixture: https://docs.pytest.org/en/latest/fixture.html
.. _GitHub: https://github.com/STScI-MESA/calibration-pipeline-testing-tool
.. _here: https://github.com/STScI-MESA/calibration-pipeline-testing-tool/pulls