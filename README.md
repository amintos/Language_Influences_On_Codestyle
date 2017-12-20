# Language_Influences_On_Codestyle

The goal of this project is to find if profession in certain programming languages influence your code style when writing other programming languages.

A (constructed) example: If we have a developer who programmed a lot of Java in his career and he now tries to write some Python code, will he make some mistakes we can classify as "typical" for a Java developer? E.g. certain naming conventions, unneeded wrapper classes ect.

## Setup

### Requirements

After cloning the project, you should install the dependencies (for python 3, make sure `pip` refers to the version for Python 3 or use `pip3`):
```bash
pip install -r requirements.txt
```

To enable linting for Python 2 files, you also need to install [pylint](http://pylint.readthedocs.io/en/latest/intro.html). (This command is under the assumption that `python` refers to a Python 2 version.)
```bash
python -m pip install pylint
```

Windows users can just use the `py` command:
```bash
py -2.7 -m pip install pylint
```

### Configuration

You need access to the [GHTorrent Database](http://ghtorrent.org/) via a Postgres server. You can configure the access to it in the config-yml file (you have to create this yourself).

Example file:

```yaml
# The database name
dbname: github
# The database user
user: user
# The database password
password: password
# The host machine where the databse is located
host: 127.0.0.1
# The port on which to reach the database (default)
port: 5432
# Your personal GitHub token for checking out the projects
github-token: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
# Your GitHub account name (which generated your token)
github-user: ghuser
# The directory to where you want to clone the projects
repo-dir: /path/to/folder/
```

## Running it

_Work in Progress_

Simply run the main file on the command line:

```bash
python3 main.py
```
