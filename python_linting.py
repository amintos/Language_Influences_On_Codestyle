import argparse
from pylint import epylint as lint


def main():
    parser = argparse.ArgumentParser(description='Lint a given python ' +
                                                 'file using pylint.')
    parser.add_argument('file', metavar='File', type=str,
                        help='the file to be analysed')

    args = parser.parse_args()
    print(args.file)
    # style_guide = flake8.get_style_guide()
    # report = style_guide.check_files('"' + args.file + '"')
    # print(report.get_statistics('N'))
    (pylint_stdout, _) = lint.py_run('"' + args.file + '" --load-plugins=pylint.extensions.mccabe --reports n',
                                     return_std=True)
    print(pylint_stdout.getvalue())

if __name__ == '__main__':
    main()
