import pytest
import argparse
import os

def run_test():
    parser = argparse.ArgumentParser(description="run test")
    parser.add_argument('--config', help='configuration file')
    # parser.add_argument('--output-dir')
    # parser.add_argument('--save_pipeline_output', help='')
    args = parser.parse_args()
    config = os.path.abspath(args.config)
    # try:
    #     os.mkdir(args.output_dir)
    #     old_dir = os.path.abspath(os.curdir)
    #     os.chdir(args.output_dir)
    # except FileExistsError:
    #     print("'{}' already exists pick a different output directory".format(args.output_dir))
    #     return

    pytest_args = ['-v']
    pytest_args += [os.path.dirname(__file__)]
    pytest_args += ['--config', config]
    pytest_args += ['--html', 'summary.html', '--self-contained-html']
    pytest.main(pytest_args)
