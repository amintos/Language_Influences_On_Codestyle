import argparse
import glob2
import os
from pylint import epylint as lint
import subprocess
import re
from collections import Counter


def main():
    parser = argparse.ArgumentParser(description='Lint a given python ' +
                                                 'file using pylint.')
    parser.add_argument('file', metavar='File', type=str,
                        help='the file to be analysed')

    args = parser.parse_args()
    print(lint_file_or_project(args.file))


def lint_file_or_project(path):
    results = Counter()
    lines_total = 0
    files = 0
    if os.path.isfile(path):
        errors, lines = lint_file(path)
        results.update(errors)
        lines_total += lines
        files = 1
    elif os.path.isdir(path):
        for filename in glob2.glob(path + '/**/*.py'):
            errors, lines = lint_file(filename)
            results.update(errors)
            lines_total += lines
            files += 1
    else:
        print('Invalid file/folder name!')
    print('{} files parsed.'.format(files))
    return results, files, lines_total


def lint_file(file):
    print('Processing ' + file)
    (pylint_stdout, _) = lint.py_run('"' + file +
                                     '" --load-plugins=pylint.extensions' +
                                     '.mccabe --reports n',
                                     return_std=True)
    output = pylint_stdout.getvalue()
    score_pos = output.find('has been rated at ')
    if score_pos < 0:
        print('Lint failed, trying to lint as python2 file')
        exit_code, _ = subprocess.getstatusoutput('py --version')
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        if exit_code:
            python2_command = 'python {}/oldlint.py {}'.format(cur_dir, file)
        else:
            python2_command = 'py {}/oldlint.py {}'.format(cur_dir, file)
        process = subprocess.Popen(python2_command.split(),
                                   stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode('utf-8')
        score_pos = output.find('has been rated at ')
        if score_pos < 0:
            print('Lint failed with python 2 and 3, skipping file.')
            return [], 0
    score_pos += 18
    score = float(output[score_pos:score_pos + 8].strip()[:-3])
    print(10.0 - score)
    # score not interesting for now, maybe later
    # still parsing it to check for success in parsing
    # print(output)
    return parse_result(output), file_len(file)


def parse_result(result):
    errors = []
    for match in re.finditer(r'((?!\()[A-Z]\d+), [^\s]+, [^\s]+', result):
        errors.append(tuple(match.group().split(',')[:2]))
    return errors


def file_len(fname):
    with open(fname) as f:
        i = -1
        for i, l in enumerate(f):
            pass
    return i + 1

if __name__ == '__main__':
    main()
