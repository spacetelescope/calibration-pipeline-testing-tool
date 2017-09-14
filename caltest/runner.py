import pytest
import argparse
import os

def run_test():
    parser = argparse.ArgumentParser(description="run test")
    parser.add_argument('--config', help='configuration file')
    args = parser.parse_args()
    print(os.path.dirname(__file__))
    pytest_args = ['-v']
    pytest_args += [os.path.dirname(__file__)]
    pytest_args += ['--config', args.config]
    pytest_args += ['--html', 'summary.html']
    pytest.main(pytest_args)