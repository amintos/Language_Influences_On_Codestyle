import sqlite3
import csv
import requests
import json
import git


class SQLiteConn():

    def __enter__(self):
        self.conn = sqlite3.connect('lics_sample.db')
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


class DBAccessor():

    LANG_PREFIX = {
        'java': 'j',
        'python': 'py',
        'cpp': 'c'
    }
    THRESH_SIGNIFICANCE = 50
    MORE_EXPERIENCE = 5

    def __init__(self):
        with SQLiteConn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE ' +
                           'type=\'table\' AND ' +
                           'name=\'lics_languages_per_author\';')
            if not cursor.fetchall():
                print('Tables not existing, creating new.')
                cursor.execute('CREATE TABLE IF NOT EXISTS lics_languages_per_author ' +
                               '(author_id INT,pychanges INT,jchanges INT,cchanges INT);')
                with open('../data/languages_per_author.csv', 'r') as fin:
                    dr = csv.DictReader(fin)
                    to_db = [(i['author_id'], i['pychanges'],
                              i['jchanges'], i['cchanges']) for i in dr]
                cursor.executemany('INSERT INTO lics_languages_per_author ' +
                                   '(author_id,pychanges,jchanges,cchanges) ' +
                                   'VALUES (?, ?, ?, ?);', to_db)

                cursor.execute('CREATE TABLE IF NOT EXISTS projects ' +
                               '(id,url,owner_id,name,description,language,' +
                               'created_at TIMESTAMP,forked_from,deleted,updated_at TIMESTAMP);')
                with open('../data/projects.csv', 'r', encoding='utf8') as fin:
                    dr = csv.DictReader(fin)
                    to_db2 = [(i['id'], i['url'],
                               i['owner_id'], i['name'],
                               i['description'], i['language'],
                               i['created_at'], i['forked_from'],
                               i['deleted'], i['updated_at']) for i in dr]

                cursor.executemany('INSERT INTO projects ' +
                                   '(id,url,owner_id,name,description,language,' +
                                   'created_at,forked_from,deleted,updated_at) ' +
                                   'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', to_db2)
                conn.commit()

    def get_candidates(self, primary_lang,
                       primary_lang2, second_lang):
        query = ('SELECT * FROM lics_languages_per_author ' +
                 'WHERE {0}changes > {3} AND (({1}changes <= {3} AND ' +
                 '{2}changes > {4}*{0}changes) OR ({2}changes <= {3} ' +
                 'AND {1}changes > {4}*{0}changes));').format(
            self.LANG_PREFIX[second_lang],
            self.LANG_PREFIX[primary_lang],
            self.LANG_PREFIX[primary_lang2],
            self.THRESH_SIGNIFICANCE,
            self.MORE_EXPERIENCE)
        result = []
        print(query)
        with SQLiteConn() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_projects_for_user(self, user_id):
        # query = ('SELECT * FROM projects WHERE id IN ' +
        #          '(SELECT repo_id FROM project_members ' +
        #          'WHERE user_id ={});').format(user_id)
        query = ('SELECT * FROM projects WHERE owner_id = \'{}\';').format(user_id)
        result = []
        with SQLiteConn() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result


def main():
    db = DBAccessor()
    candidates = db.get_candidates('python', 'java', 'cpp')
    for candidate in candidates:
        sample_projects = db.get_projects_for_user(candidate[0])
        if sample_projects:
            break
    sample_project = sample_projects[1]
    print(sample_project)
    clone_project(sample_project[1], sample_project[3], 'repos')


def clone_project(url, name, file_path):
    r = requests.get(url)
    obj = json.loads(r.text)
    if 'clone_url' in obj.keys():
        git.Repo.clone_from(obj['clone_url'], file_path + '/' + name)
    else:
        print('invalid repo')

if __name__ == '__main__':
    main()
