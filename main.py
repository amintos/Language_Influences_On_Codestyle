import requests
import json
import git
import string
import yaml
import os
from .dbaccessor import DBAccessor
from .pythonlinting import lint_file_or_project


def format_filename(s):
    """Take a string and return a valid filename constructed from it."""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def main():
    with open('config.yml', 'r') as cfg:
        config = yaml.load(cfg)

    db = DBAccessor(config)
    candidates = db.get_candidates('cpp', 'java', 'python')
    print('{} candidates found.'.format(len(candidates)))

    sample_projects = set()
    for candidate in candidates:
        projects = db.get_projects_for_user(candidate[0], 'python')
        if projects:
            sample_projects.update(projects)
    print('{} projects for these candidates found.'
          .format(len(sample_projects)))

    token = config['github-token']
    existing_projects = []
    for project in sample_projects:
        r = requests.get(project[1], auth=('shorschig', token))
        obj = json.loads(r.text)
        if 'clone_url' in obj.keys():
            existing_projects.append((obj['clone_url'], project[3]))
    print('{} projects are reachable.'
          .format(len(existing_projects)))

    print('Cloning repositories...')
    for clone_url, name in existing_projects:
        git.Repo.clone_from(clone_url, config['repo-dir'] +
                            format_filename(name))
    print('Finished cloning.')

    print('Linting projects:')
    for project_dir in os.listdir(config['repo-dir']):
        error_codes, num_files = lint_file_or_project(project_dir)
        print(error_codes)

if __name__ == '__main__':
    main()
