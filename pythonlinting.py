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
    files = 0
    if os.path.isfile(path):
        results.update(lint_file(path))
        files = 1
    elif os.path.isdir(path):
        for filename in glob.iglob(path + '**/*.py', recursive=True):
            results.update(lint_file(filename))
            files += 1
    else:
        print('Invalid file/folder name!')
    print('{} files parsed.'.format(files))
    return results, files


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
        if exit_code:
            python2_command = 'python oldlint.py {}'.format(file)
        else:
            python2_command = 'py oldlint.py {}'.format(file)
        process = subprocess.Popen(python2_command.split(),
                                   stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode('utf-8')
        score_pos = output.find('has been rated at ')
    score_pos += 18
    score = float(output[score_pos:score_pos + 8].strip()[:-3])
    print(10.0 - score)
    # score not interesting for now, maybe later
    # still parsing it to check for success in parsing
    # print(output)
    return parse_result(output)


def parse_result(result):
    errors = []
    for match in re.finditer(r'((?!\()[A-Z]\d+), [^\s]+, [^\s]+', result):
        errors.append(tuple(match.group().split(',')[:2]))
    return errors

if __name__ == '__main__':
    main()
