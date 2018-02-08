"""Linter wrapping PyLint to analyze python2 or python3 projects.

The goal with this linter was not only to provide a method to execute PyLint
no matter what python version the file is, it also parses its output to a
better useable format.

"""
import argparse
import glob2
import os
from pylint import epylint as lint
import subprocess
import re
from collections import Counter, namedtuple

ErrorCode = namedtuple('ErrorCode', ['code', 'description'])


def main():
    """Lint a file given via argument."""
    parser = argparse.ArgumentParser(description='Lint a given python ' +
                                                 'file using pylint.')
    parser.add_argument('file', metavar='File', type=str,
                        help='the file to be analysed')
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)

    args = parser.parse_args()
    print(lint_file_or_project(args.file, args.verbose))


def lint_file_or_project(path, verbose=False):
    """Lint input, file or project.

    Args:

    path: Path to a file or a folder (python project).

    Returns:

    A tuple, consisting of:
        - results: Parsed output of PyLint. A Counter of error codes
                   (tuple with the properties 'code' and 'description')
        - files: The number of files parsed in total.
        - lines_total: The number of lines parsed total.
    """
    results = Counter()
    lines_total = 0
    files = 0
    if os.path.isfile(path):
        errors, lines = lint_file(path, verbose)
        results.update(errors)
        lines_total += lines
        files = 1
    elif os.path.isdir(path):
        for filename in glob2.glob(path + '/**/*.py'):
            errors, lines = lint_file(filename, verbose)
            results.update(errors)
            lines_total += lines
            files += 1
    else:
        print('Invalid file/folder name!')
    if verbose:
        print('{} files parsed.'.format(files))
        print('{} lines total.'.format(lines_total))
    return results, files, lines_total


def lint_file(file, verbose=False):
    """Lint input file.

    Args:

    path: Path to a file.

    Returns:

    A tuple, consisting of:
        - results: Parsed output of PyLint. A Counter of error codes
                   (tuple with the properties 'code' and 'description')
        - lines_total: The number of lines parsed total.
    """
    if verbose:
        print('Processing ' + file)
    (pylint_stdout, _) = lint.py_run('"' + file +
                                     '" --load-plugins=pylint.extensions' +
                                     '.mccabe --reports n',
                                     return_std=True)
    output = pylint_stdout.getvalue()
    score_pos = output.find('has been rated at ')
    if score_pos < 0:
        if verbose:
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
            if verbose:
                print('Lint failed with python 2 and 3, skipping file.')
            return [], 0
    score_pos += 18
    score = float(output[score_pos:score_pos + 8].strip()[:-3])
    if verbose:
        print('File scored at {}'.format(score))
    # score not interesting for now, maybe later
    # still parsing it to check for success in parsing
    return parse_result(output), file_len(file)


def parse_result(result):
    """Parse PyLint output.

    Args:

    result: stdout of PyLint. Should be a string in the form of
            'test.py:77: convention (C0305, trailing-newlines, )
                                                Trailing newlines
            test.py:1: convention (C0111, missing-docstring, )
                                                Missing module docstring'
            or something similar.
    file: The name of the file which was analyzed. Used for output.

    Returns:

    A list of triples,
    """
    errors = []
    for match in re.finditer(r'((?!\()[A-Z]\d+), [^\s]+, [^\s]+', result):
        errors.append(ErrorCode(*match.group().split(',')[:2]))
    return errors


def file_len(fname):
    """Get the number of lines in a file, trying ASCII encoding."""
    i = -1
    try:
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
    except UnicodeDecodeError:
        print('Error opening file, trying utf-8')
        return file_len_utf8(fname)
    return i + 1


def file_len_utf8(fname):
    """Get the number of lines in a file, trying UTF-8 encoding."""
    i = -1
    try:
        with open(fname, encoding="utf-8") as f:
            for i, l in enumerate(f):
                pass
    except:
        print('Unicode doesn\'t work either, skipping number of lines for now')
    return i + 1

if __name__ == '__main__':
    main()
