import pytest
from astropy.io import fits
from datetime import datetime
from py.xml import html
import jwst
import crds
import json
import os
import re

def pytest_addoption(parser):
    parser.addoption("--config",
                     help=("Input files to test"))


def pytest_configure(config):
    config._metadata['jwst'] = jwst.__version__
    config._metadata['crds_context'] = crds.heavy_client.get_processing_mode('jwst')[1]


def pytest_runtest_setup(item):
    # read the JSON config
    if item.config.getoption("config"):
        with open(item.config.option.config) as config_file:
            config = json.load(config_file)

    # get the name of the step being testing in current module
    module, ext = os.path.splitext(item.fspath.basename)
    module = module.replace('test_', '')

    # skip the tests for this step if no data was supplied
    if module not in config.keys():
        pytest.skip("No {} section in config".format(module))


def pytest_generate_tests(metafunc):
    with open(metafunc.config.option.config) as config_file:
        config = json.load(config_file)
    steps = ['dq_init', 'saturation', 'superbias', 'persistence',
             'linearity', 'dark_current', 'jump', 'ramp_fit',
             'assign_wcs']
    # parametrize tests with the input files supplied for that step
    for step in steps:
        if step in metafunc.module.__name__ and config.get(step):
            if step != "persistence":
                metafunc.parametrize("input_file", config[step], scope='module')
            else:
                metafunc.parametrize(["input_file","trapsfilled"], config[step], scope='module')

@pytest.fixture(scope='module')
def fits_input(input_file):
    # open the input_file defined above once for each module
    yield fits.open(input_file)


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(0, html.th('Time', class_='sortable time', col='time'))
    cells.insert(1, html.th('Test', class_='sortable', col='shortname'))
    cells.insert(1, html.th('Module', class_='sortable', col='shortname'))
    cells.pop()
    cells.pop(-2)
    cells.insert(3,html.th('Input Data', class_='sortable', col='data'))


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    # get name of input file from test name
    full_string = report.nodeid
    module = full_string.split('::')[0].split('/')[-1][:-3].replace('test_', '')
    test = full_string.split('::')[1].split('[')[0]
    if '[' in full_string:
        data = full_string.split('::')[1].split('[')[-1][:-1]
    else:
        data = ''

    cells.insert(0, html.td(datetime.utcnow(), class_='col-time'))
    cells.insert(1, html.td(test, class_='col-time'))
    cells.insert(1, html.td(module, class_='col-time'))
    cells.pop()
    cells.pop(-2)
    cells.insert(3, html.td(data, class_='col-time'))

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    if report.when == 'call':
        # get filename between square brackets
        m = re.match('^.*\[(.*)\].*$', item.name)
        fname = item.name.split('[')[0]+'_'+m.group(1).split('/')[-1][:-5]+'.png'
        # always add url to report
        if os.path.isfile(fname):
            # add plot if it exists
            extra.append(pytest_html.extras.image(fname))
        report.extra = extra
