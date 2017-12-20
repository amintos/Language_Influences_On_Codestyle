#!python2
from pylint import epylint as lint
import argparse


parser = argparse.ArgumentParser(description='Lint a given python ' +
                                             'file using pylint.')
parser.add_argument('file', metavar='File', type=str,
                    help='the file to be analysed')

args = parser.parse_args()
file = args.file

(pylint_stdout, _) = lint.py_run('"' + file +
                                 '" --load-plugins=pylint.extensions' +
                                 '.mccabe --reports n',
                                 return_std=True)
output = pylint_stdout.getvalue()
print(output)
