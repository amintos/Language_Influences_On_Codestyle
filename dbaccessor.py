import psycopg2


class PSQLConn():

    def __init__(self, cfg):
        self._cfg = cfg

    def __enter__(self):
        self.conn = psycopg2.connect(dbname=self._cfg['dbname'],
                                     user=self._cfg['user'],
                                     password=self._cfg['password'],
                                     host=self._cfg['host'],
                                     port=self._cfg['port'])
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


class DBAccessor():

    LANG_PREFIX = {
        'java': 'j',
        'python': 'py',
        'cpp': 'c'
    }
    THRESH_SIGNIFICANCE = 150
    MORE_EXPERIENCE = 5

    def __init__(self, cfg):
        self._cfg = cfg

    def get_candidates(self, primary_lang,
                       primary_lang2, second_lang, thresh=THRESH_SIGNIFICANCE,
                       exp=MORE_EXPERIENCE):
        query = ('SELECT * FROM lics_languages_per_author ' +
                 'WHERE {0}changes > {3} AND (({1}changes <= {3} AND ' +
                 '{2}changes > {4}*{0}changes) OR ({2}changes <= {3} ' +
                 'AND {1}changes > {4}*{0}changes));').format(
            self.LANG_PREFIX[second_lang],
            self.LANG_PREFIX[primary_lang],
            self.LANG_PREFIX[primary_lang2],
            thresh,
            exp)
        result = []
        with PSQLConn(self._cfg) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    def get_projects_for_user(self, user_id, lang=None):
        query = ('SELECT url, name FROM projects WHERE id IN ' +
                 '(SELECT repo_id FROM project_members ' +
                 'WHERE user_id =\'{}\')').format(user_id)
        if lang:
            query += 'AND LOWER(language) LIKE LOWER(\'{}\')'.format(lang)
        result = []
        with PSQLConn(self._cfg) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result
